# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ApprovalRule(models.Model):
    """
    Configurable Approval Rules based on request type, thresholds, and groups.
    This acts as a dynamic matrix over the hardcoded GM -> MD pipeline if configured.
    """
    _name = 'nn.fund.approval.rule'
    _description = 'Configurable Approval Rule'
    _order = 'sequence, min_amount'
    _check_company_auto = True

    name = fields.Char(string='Rule Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

    request_type = fields.Selection([
        ('allocation', 'Allocation'),
        ('requisition', 'Requisition'),
        ('transfer', 'Transfer')
    ], string='Request Type', required=True)

    min_amount = fields.Monetary(string='Minimum Amount', currency_field='currency_id', required=True)
    max_amount = fields.Monetary(string='Maximum Amount', currency_field='currency_id', required=True)
    
    sequence = fields.Integer(string='Priority Sequence', default=10)

    # Simplified representation: which groups are required?
    require_gm = fields.Boolean(string='Requires GM Approval', default=True)
    require_finance = fields.Boolean(string='Requires Finance Approval', default=False)
    require_md = fields.Boolean(string='Requires MD Approval', default=False)

    def _get_required_approvals(self, request_type, amount):
        """
        Evaluate which approvals are required for a given type and amount.
        """
        rule = self.search([
            ('request_type', '=', request_type),
            ('min_amount', '<=', amount),
            '|', ('max_amount', '>=', amount), ('max_amount', '=', 0.0)
        ], order='sequence asc', limit=1)

        if rule:
            return {
                'gm': rule.require_gm,
                'finance': rule.require_finance,
                'md': rule.require_md
            }
        # Fallback to standard hardcoded pipeline
        return {'gm': True, 'finance': False, 'md': True}
