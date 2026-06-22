# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re
import logging

_logger = logging.getLogger(__name__)

class BankEmailIntegration(models.Model):
    """
    Prototype to parse incoming bank notification emails and create incoming fund records.
    """
    _name = 'nn.bank.email.integration'
    _description = 'Bank Email Parser'
    _inherit = ['mail.thread']

    name = fields.Char(string='Subject', required=True)
    message_id = fields.Char(string='Email Message ID', readonly=True)
    parsed_status = fields.Selection([
        ('pending', 'Pending Parsing'),
        ('success', 'Successfully Parsed'),
        ('failed', 'Parsing Failed')
    ], string='Parse Status', default='pending')
    
    log = fields.Text(string='Processing Log')

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """
        Override message_new to handle incoming emails sent to the alias.
        """
        defaults = custom_values or {}
        defaults['name'] = msg_dict.get('subject', 'No Subject')
        defaults['message_id'] = msg_dict.get('message_id')
        
        record = super(BankEmailIntegration, self).message_new(msg_dict, defaults)
        record._parse_email_body(msg_dict.get('body', ''))
        return record

    def _parse_email_body(self, body):
        self.ensure_one()
        # Prototype Regex patterns
        # Example body: "Bank XYZ: You received BDT 50,000.00 from Sender123 on 2026-06-22. Ref: TXN9999"
        try:
            amount_match = re.search(r'(?:BDT|USD|EUR)\s*([\d,]+\.?\d*)', body)
            ref_match = re.search(r'Ref:\s*([A-Za-z0-9]+)', body)
            sender_match = re.search(r'from\s+([A-Za-z0-9\s]+)\s+on', body)

            if amount_match and ref_match:
                amount = float(amount_match.group(1).replace(',', ''))
                ref = ref_match.group(1)
                sender = sender_match.group(1).strip() if sender_match else 'Unknown'

                # Try to find default fund account
                account = self.env['nn.fund.account'].search([], limit=1)
                if not account:
                    raise ValueError("No Fund Account exists to assign the money to.")

                # Check duplicate ref
                existing = self.env['nn.incoming.fund'].search([('name', '=', ref), ('fund_account_id', '=', account.id)])
                if existing:
                    raise ValueError(f"Duplicate Transaction Reference {ref} detected.")

                # Create incoming fund in pending_verification state
                self.env['nn.incoming.fund'].create({
                    'name': ref,
                    'fund_account_id': account.id,
                    'amount': amount,
                    'sender': sender,
                    'description': f"Auto-created from email. Message ID: {self.message_id}",
                    'state': 'pending_verification'
                })
                
                self.write({
                    'parsed_status': 'success',
                    'log': f"Successfully parsed {amount} with Ref {ref}"
                })
            else:
                raise ValueError("Could not extract amount or reference from the email body.")

        except Exception as e:
            self.write({
                'parsed_status': 'failed',
                'log': str(e)
            })
            _logger.error(f"Bank Email Parsing Failed: {str(e)}")
            # Create a notification activity for the administrator
            users = self.env.ref('nn_fund_management.group_fund_administrator').users
            for user in users:
                self.activity_schedule(
                    'mail.mail_activity_data_warning',
                    user_id=user.id,
                    note=f'Failed to parse incoming bank email: {str(e)}'
                )
