# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class FundAllocation(models.Model):
    """
    Allocates funds from a Fund Account to a Project or Expense Head.
    """
    _name = 'nn.fund.allocation'
    _description = 'Fund Allocation Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(string='Request Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    fund_account_id = fields.Many2one('nn.fund.account', string='Fund Account', required=True, check_company=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', related='fund_account_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    target_id = fields.Many2one('nn.project.expense.head', string='Project / Expense Head', required=True, check_company=True, tracking=True)
    target_type = fields.Selection(related='target_id.target_type', string='Target Type')

    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id', tracking=True)
    purpose = fields.Text(string='Purpose', required=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today)
    requested_by_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, tracking=True)
    attachment = fields.Binary(string='Attachment')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('gm_approved', 'GM Approved'),
        ('md_approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.fund.allocation') or _('New')
        return super(FundAllocation, self).create(vals_list)

    @api.constrains('amount', 'fund_account_id')
    def _check_amount(self):
        """
        Validate allocation constraints.
        Note: The actual double-spend check is handled by the Fund Account's _check_available_balance constraint,
        which will trigger when the state changes and amount_on_hold computes.
        But we can do an early check here.
        """
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("Allocation amount must be strictly positive."))
            if record.state == 'draft' and record.amount > record.fund_account_id.available_unassigned_balance:
                raise ValidationError(_("Requested amount exceeds the available unassigned balance in the selected Fund Account."))

    def action_submit(self):
        for record in self:
            if record.amount > record.fund_account_id.available_unassigned_balance:
                raise UserError(_("Cannot submit. Insufficient unassigned balance."))
            record._write_audit_history('Submitted')
            record.state = 'submitted'

    def action_gm_approve(self):
        for record in self:
            record._write_audit_history('GM Approved')
            record.state = 'gm_approved'

    def action_md_approve(self):
        for record in self:
            record._write_audit_history('MD Approved')
            record.state = 'md_approved'

    def action_reject(self):
        for record in self:
            record._write_audit_history('Rejected')
            record.state = 'rejected'

    def action_cancel(self):
        for record in self:
            if record.state == 'md_approved':
                raise UserError(_("Cannot cancel an already approved allocation directly without reversal process."))
            record._write_audit_history('Cancelled')
            record.state = 'cancelled'

    def _write_audit_history(self, action_name):
        self.ensure_one()
        self.env['nn.audit.history'].create({
            'res_model': self._name,
            'res_id': self.id,
            'action': action_name,
            'amount': self.amount,
            'user_id': self.env.user.id,
            'old_state': self.state,
            'comments': f"Action {action_name} executed."
        })
