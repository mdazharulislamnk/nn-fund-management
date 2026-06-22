# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMoveBill(models.Model):
    """
    Custom Bill model to represent Vendor Bills posted against approved requisitions.
    In a real implementation, this might inherit 'account.move', but per requirements, 
    we are building a controlled custom bill model to ensure strict adherence.
    """
    _name = 'nn.account.move.bill'
    _description = 'Fund Bill Control'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(string='Bill Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    
    requisition_id = fields.Many2one('nn.fund.requisition', string='Requisition', required=True, check_company=True, domain=[('state', 'in', ['md_approved', 'closed'])])
    target_id = fields.Many2one('nn.project.expense.head', string='Project / Expense Head', related='requisition_id.target_id', store=True)
    
    company_id = fields.Many2one('res.company', string='Company', related='requisition_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    amount = fields.Monetary(string='Billed Amount', required=True, currency_field='currency_id', tracking=True)
    date = fields.Date(string='Bill Date', default=fields.Date.context_today)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.account.move.bill') or _('New')
        return super(AccountMoveBill, self).create(vals_list)

    @api.constrains('amount', 'requisition_id')
    def _check_bill_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("Bill amount must be strictly positive."))
            
            # The remaining amount should consider this bill's amount if it's already posted
            # Or if it's a new bill trying to be posted, we need to ensure it doesn't exceed 
            # the remaining billable balance of the requisition.
            if record.state == 'draft':
                # Check against current remaining
                if record.amount > record.requisition_id.remaining_billable_amount:
                    raise ValidationError(_(
                        "Billed amount (%(amount)s) cannot exceed the remaining billable amount (%(rem)s) of the requisition.",
                        amount=record.amount, rem=record.requisition_id.remaining_billable_amount
                    ))

    def action_post(self):
        for record in self:
            if record.requisition_id.state not in ['md_approved', 'closed']:
                raise UserError(_("Cannot post a bill for a non-approved requisition."))
            if record.amount > record.requisition_id.remaining_billable_amount:
                raise UserError(_("Cannot post. Billed amount exceeds remaining billable amount."))
            
            record.state = 'posted'

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
