# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class FundTransfer(models.Model):
    """
    Handles transfers between projects and expense heads.
    """
    _name = 'nn.fund.transfer'
    _description = 'Fund Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(string='Transfer Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    
    source_id = fields.Many2one('nn.project.expense.head', string='Source', required=True, check_company=True, tracking=True)
    destination_id = fields.Many2one('nn.project.expense.head', string='Destination', required=True, check_company=True, tracking=True)
    
    company_id = fields.Many2one('res.company', string='Company', related='source_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id', tracking=True)
    reason = fields.Text(string='Reason', required=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today)
    requested_by_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, tracking=True)
    
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
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.fund.transfer') or _('New')
        return super(FundTransfer, self).create(vals_list)

    @api.constrains('source_id', 'destination_id')
    def _check_source_dest(self):
        for record in self:
            if record.source_id == record.destination_id:
                raise ValidationError(_("Source and Destination cannot be the same."))

    @api.constrains('amount', 'source_id')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("Transfer amount must be strictly positive."))
            if record.state == 'draft' and record.amount > record.source_id.available_fund:
                raise ValidationError(_("Transfer amount exceeds the source's available fund."))

    def action_submit(self):
        for record in self:
            if record.amount > record.source_id.available_fund:
                raise UserError(_("Cannot submit. Insufficient available fund in source."))
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
                raise UserError(_("Cannot cancel an already approved transfer directly."))
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
