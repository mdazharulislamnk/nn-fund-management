# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AuditHistory(models.Model):
    """
    Model strictly for preserving history of financial actions.
    """
    _name = 'nn.audit.history'
    _description = 'Financial Audit History'
    _order = 'create_date desc'

    res_model = fields.Char(string='Model Name', required=True, index=True)
    res_id = fields.Integer(string='Record ID', required=True, index=True)
    
    user_id = fields.Many2one('res.users', string='Executed By', default=lambda self: self.env.user, required=True)
    action = fields.Char(string='Action Taken', required=True)
    old_state = fields.Char(string='Previous State')
    
    amount = fields.Float(string='Associated Amount')
    comments = fields.Text(string='Comments')
    
    date = fields.Datetime(string='Date & Time', default=fields.Datetime.now, required=True)
    
    @api.model
    def create(self, vals):
        # Prevent manual creation from UI by typical users? Handled via security rules.
        return super(AuditHistory, self).create(vals)
