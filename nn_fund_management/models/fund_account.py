# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class FundAccount(models.Model):
    """
    Model representing financial accounts (bank/cash) holding incoming funds.
    """
    _name = 'nn.fund.account'
    _description = 'Fund Account'
    _check_company_auto = True

    name = fields.Char(string='Account Name', required=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', readonly=True)

    # Funds records related to this account
    incoming_fund_ids = fields.One2many('nn.incoming.fund', 'fund_account_id', string='Incoming Funds')
    allocation_ids = fields.One2many('nn.fund.allocation', 'fund_account_id', string='Allocations')

    # Computed Balances
    total_received = fields.Monetary(string='Total Received', compute='_compute_balances', store=True, currency_field='currency_id', help='Total funds confirmed as received.')
    amount_on_hold = fields.Monetary(string='Amount on Hold', compute='_compute_balances', store=True, currency_field='currency_id', help='Funds currently locked in pending allocations.')
    total_assigned_amount = fields.Monetary(string='Total Assigned Amount', compute='_compute_balances', store=True, currency_field='currency_id', help='Funds successfully allocated to projects or expense heads.')
    available_unassigned_balance = fields.Monetary(string='Available Unassigned Balance', compute='_compute_balances', store=True, currency_field='currency_id', help='total_received - amount_on_hold - total_assigned_amount.')

    @api.depends('incoming_fund_ids.amount', 'incoming_fund_ids.state', 
                 'allocation_ids.amount', 'allocation_ids.state')
    def _compute_balances(self):
        """
        Dynamically calculate financial balances based on related incoming funds and allocations.
        Ensures exact consistency and prevents double spending.
        """
        for account in self:
            # 1. Calculate Total Received from Confirmed Incoming Funds
            confirmed_incoming = account.incoming_fund_ids.filtered(lambda x: x.state == 'confirmed')
            total_rcvd = sum(confirmed_incoming.mapped('amount'))
            
            # 2. Calculate Amount on Hold (Allocations that are submitted but not yet approved/rejected/cancelled)
            hold_allocations = account.allocation_ids.filtered(lambda x: x.state in ('submitted', 'gm_approved'))
            amount_held = sum(hold_allocations.mapped('amount'))
            
            # 3. Calculate Total Assigned Amount (Allocations that are fully approved)
            approved_allocations = account.allocation_ids.filtered(lambda x: x.state == 'md_approved')
            total_assigned = sum(approved_allocations.mapped('amount'))
            
            # 4. Calculate Available Unassigned Balance
            available_balance = total_rcvd - amount_held - total_assigned

            account.total_received = total_rcvd
            account.amount_on_hold = amount_held
            account.total_assigned_amount = total_assigned
            account.available_unassigned_balance = available_balance

    @api.constrains('available_unassigned_balance')
    def _check_available_balance(self):
        """
        Safety constraint to ensure the unassigned balance never drops below zero.
        """
        for account in self:
            if account.available_unassigned_balance < 0.0:
                raise ValidationError(_("The Available Unassigned Balance for account '%s' cannot be negative.", account.name))


class IncomingFund(models.Model):
    """
    Model representing incoming money to a fund account.
    """
    _name = 'nn.incoming.fund'
    _description = 'Incoming Fund Transaction'
    _check_company_auto = True

    name = fields.Char(string='Transaction Reference', required=True, copy=False)
    fund_account_id = fields.Many2one('nn.fund.account', string='Fund Account', required=True, check_company=True)
    company_id = fields.Many2one('res.company', string='Company', related='fund_account_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    sender = fields.Char(string='Sender/Source', required=True)
    description = fields.Text(string='Description')
    attachment = fields.Binary(string='Attachment')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_verification', 'Pending Verification'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    _sql_constraints = [
        ('unique_transaction_ref', 'UNIQUE(fund_account_id, name)', 'The transaction reference must be unique within the same fund account!')
    ]

    def action_confirm(self):
        """
        Confirm the incoming fund transaction. This will add to the account's total received.
        """
        for record in self:
            if record.amount <= 0:
                raise UserError(_("Amount must be strictly positive."))
            record.state = 'confirmed'

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
