# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectExpenseHead(models.Model):
    """
    Model abstracting the target for fund allocations (can be a Project or Expense Head).
    """
    _name = 'nn.project.expense.head'
    _description = 'Project / Expense Head Target'
    _check_company_auto = True

    name = fields.Char(string='Name', required=True)
    target_type = fields.Selection([
        ('project', 'Project'),
        ('expense_head', 'Expense Head')
    ], string='Target Type', required=True, default='project')
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    # Relationships to trace balances
    allocation_ids = fields.One2many('nn.fund.allocation', 'target_id', string='Allocations')
    requisition_ids = fields.One2many('nn.fund.requisition', 'target_id', string='Requisitions')
    bill_ids = fields.One2many('nn.account.move.bill', 'target_id', string='Bills')
    incoming_transfer_ids = fields.One2many('nn.fund.transfer', 'destination_id', string='Incoming Transfers')
    outgoing_transfer_ids = fields.One2many('nn.fund.transfer', 'source_id', string='Outgoing Transfers')

    # Computed Balances
    total_allocated_fund = fields.Monetary(string='Total Allocated Fund', compute='_compute_balances', store=True, currency_field='currency_id')
    available_fund = fields.Monetary(string='Available Fund', compute='_compute_balances', store=True, currency_field='currency_id')
    requisition_hold = fields.Monetary(string='Requisition Hold', compute='_compute_balances', store=True, currency_field='currency_id')
    transfer_hold = fields.Monetary(string='Transfer Hold', compute='_compute_balances', store=True, currency_field='currency_id')
    approved_unspent_amount = fields.Monetary(string='Approved Unspent Amount', compute='_compute_balances', store=True, currency_field='currency_id')
    total_spent_amount = fields.Monetary(string='Total Spent Amount', compute='_compute_balances', store=True, currency_field='currency_id')
    total_incoming_transfers = fields.Monetary(string='Incoming Transfers', compute='_compute_balances', store=True, currency_field='currency_id')
    total_outgoing_transfers = fields.Monetary(string='Outgoing Transfers', compute='_compute_balances', store=True, currency_field='currency_id')

    @api.depends(
        'allocation_ids.amount', 'allocation_ids.state',
        'requisition_ids.requested_amount', 'requisition_ids.state',
        'bill_ids.amount', 'bill_ids.state',
        'incoming_transfer_ids.amount', 'incoming_transfer_ids.state',
        'outgoing_transfer_ids.amount', 'outgoing_transfer_ids.state'
    )
    def _compute_balances(self):
        """
        Dynamically calculate financial balances based on related allocations, requisitions, bills, and transfers.
        """
        for target in self:
            # 1. Total Allocated Fund (Approved allocations to this target)
            approved_allocations = target.allocation_ids.filtered(lambda x: x.state == 'md_approved')
            total_allocated = sum(approved_allocations.mapped('amount'))

            # 2. Transfers
            approved_incoming_transfers = target.incoming_transfer_ids.filtered(lambda x: x.state == 'md_approved')
            incoming_transfers = sum(approved_incoming_transfers.mapped('amount'))
            
            approved_outgoing_transfers = target.outgoing_transfer_ids.filtered(lambda x: x.state == 'md_approved')
            outgoing_transfers = sum(approved_outgoing_transfers.mapped('amount'))

            pending_outgoing_transfers = target.outgoing_transfer_ids.filtered(lambda x: x.state in ('submitted', 'gm_approved'))
            transfer_hold = sum(pending_outgoing_transfers.mapped('amount'))

            # 3. Requisition Holds (Pending Requisitions)
            pending_requisitions = target.requisition_ids.filtered(lambda x: x.state in ('submitted', 'gm_approved'))
            req_hold = sum(pending_requisitions.mapped('requested_amount'))

            # 4. Approved Unspent Amount (Approved Requisition Amount minus Billed Amount)
            approved_requisitions = target.requisition_ids.filtered(lambda x: x.state in ('md_approved', 'closed'))
            approved_unspent = sum(approved_requisitions.mapped('remaining_billable_amount'))

            # 5. Total Spent Amount (Posted Bills)
            posted_bills = target.bill_ids.filtered(lambda x: x.state == 'posted')
            total_spent = sum(posted_bills.mapped('amount'))

            # 6. Available Fund
            # Total Allocation + Incoming Transfers - Outgoing Transfers - Transfer Hold - Requisition Hold - Approved Requisition Total (which includes Unspent + Spent from that requisition)
            # Actually, when a requisition is approved, its total requested amount is deducted from available_fund permanently.
            # So: Available = (Total Allocated + Incoming Transfers) - (Outgoing Transfers + Transfer Hold) - (Requisition Hold + Total Approved Requisition Amounts)
            total_approved_reqs = sum(approved_requisitions.mapped('requested_amount'))
            available_balance = (total_allocated + incoming_transfers) - (outgoing_transfers + transfer_hold) - (req_hold + total_approved_reqs)

            target.total_allocated_fund = total_allocated
            target.total_incoming_transfers = incoming_transfers
            target.total_outgoing_transfers = outgoing_transfers
            target.transfer_hold = transfer_hold
            target.requisition_hold = req_hold
            target.approved_unspent_amount = approved_unspent
            target.total_spent_amount = total_spent
            target.available_fund = available_balance

    @api.constrains('available_fund')
    def _check_available_fund(self):
        """
        Ensure available fund does not go negative.
        """
        for target in self:
            if target.available_fund < 0.0:
                raise ValidationError(_("The Available Fund for '%s' cannot be negative. This action would result in an overspend or invalid transfer.", target.name))
