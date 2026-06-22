# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class FundRequisition(models.Model):
    """
    Model for requesting funds from a specific Project or Expense Head.
    """
    _name = 'nn.fund.requisition'
    _description = 'Fund Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(string='Requisition Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    target_id = fields.Many2one('nn.project.expense.head', string='Project / Expense Head', required=True, check_company=True, tracking=True)
    target_type = fields.Selection(related='target_id.target_type', string='Target Type')

    company_id = fields.Many2one('res.company', string='Company', related='target_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    requested_amount = fields.Monetary(string='Requested Amount', required=True, currency_field='currency_id', tracking=True)
    remaining_billable_amount = fields.Monetary(string='Remaining Billable Amount', compute='_compute_billable_amount', store=True, currency_field='currency_id')
    
    purpose = fields.Text(string='Purpose', required=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.context_today)
    required_date = fields.Date(string='Required Date')
    requested_by_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, tracking=True)
    attachment = fields.Binary(string='Supporting Attachment')
    
    bill_ids = fields.One2many('nn.account.move.bill', 'requisition_id', string='Bills')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('gm_approved', 'GM Approved'),
        ('md_approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed')
    ], string='Status', default='draft', required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('nn.fund.requisition') or _('New')
        return super(FundRequisition, self).create(vals_list)

    @api.depends('requested_amount', 'bill_ids.amount', 'bill_ids.state')
    def _compute_billable_amount(self):
        """
        Calculates remaining amount available to be billed against this requisition.
        """
        for req in self:
            if req.state in ('md_approved', 'closed'):
                posted_bills = req.bill_ids.filtered(lambda x: x.state == 'posted')
                total_billed = sum(posted_bills.mapped('amount'))
                req.remaining_billable_amount = req.requested_amount - total_billed
            else:
                req.remaining_billable_amount = 0.0

    @api.constrains('requested_amount', 'target_id')
    def _check_amount(self):
        for record in self:
            if record.requested_amount <= 0:
                raise ValidationError(_("Requisition amount must be strictly positive."))
            if record.state == 'draft' and record.requested_amount > record.target_id.available_fund:
                raise ValidationError(_("Requested amount exceeds the available fund in the selected Project/Expense Head."))

    def action_submit(self):
        for record in self:
            if record.requested_amount > record.target_id.available_fund:
                raise UserError(_("Cannot submit. Insufficient available fund."))
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
            if record.state in ('md_approved', 'closed'):
                raise UserError(_("Cannot cancel an already approved requisition directly."))
            record._write_audit_history('Cancelled')
            record.state = 'cancelled'

    def action_close(self):
        for record in self:
            if record.state != 'md_approved':
                raise UserError(_("Only approved requisitions can be closed."))
            record._write_audit_history('Closed')
            record.state = 'closed'

    def _write_audit_history(self, action_name):
        self.ensure_one()
        self.env['nn.audit.history'].create({
            'res_model': self._name,
            'res_id': self.id,
            'action': action_name,
            'amount': self.requested_amount,
            'user_id': self.env.user.id,
            'old_state': self.state,
            'comments': f"Action {action_name} executed."
        })
