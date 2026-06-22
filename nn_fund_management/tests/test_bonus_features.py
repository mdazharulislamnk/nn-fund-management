# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestBonusFeatures(TransactionCase):

    def setUp(self):
        super(TestBonusFeatures, self).setUp()
        self.FundAccount = self.env['nn.fund.account'].create({
            'name': 'Main Bank Account for Email',
            'account_number': 'EMAIL_123'
        })

    def test_01_bank_email_parsing(self):
        """Test the regex parsing prototype for incoming bank emails."""
        
        email_body = "Bank XYZ: You received BDT 75,500.50 from JohnDoe on 2026-06-22. Ref: TXN999ABC"
        
        msg_dict = {
            'subject': 'Bank Alert',
            'message_id': '<12345@bank.com>',
            'body': email_body
        }
        
        # Simulate incoming email creation
        integration = self.env['nn.bank.email.integration'].message_new(msg_dict)
        
        # Check if parsing was successful
        self.assertEqual(integration.parsed_status, 'success')
        
        # Verify the incoming fund record was created in 'pending_verification'
        incoming = self.env['nn.incoming.fund'].search([('name', '=', 'TXN999ABC')])
        self.assertTrue(incoming)
        self.assertEqual(incoming.amount, 75500.50)
        self.assertEqual(incoming.sender, 'JohnDoe')
        self.assertEqual(incoming.state, 'pending_verification')

    def test_02_approval_rule_logic(self):
        """Test dynamic approval rules evaluation."""
        
        # Create a rule for allocations under 50,000 to only require GM
        self.env['nn.fund.approval.rule'].create({
            'name': 'Low Level Allocation',
            'request_type': 'allocation',
            'min_amount': 0.0,
            'max_amount': 50000.0,
            'require_gm': True,
            'require_md': False,
            'sequence': 5
        })
        
        # Create a rule for > 50,000 requiring MD
        rule_model = self.env['nn.fund.approval.rule']
        rule_model.create({
            'name': 'High Level Allocation',
            'request_type': 'allocation',
            'min_amount': 50000.01,
            'max_amount': 9999999.0,
            'require_gm': True,
            'require_md': True,
            'sequence': 10
        })
        
        # Evaluate for 30,000
        req_low = rule_model._get_required_approvals('allocation', 30000.0)
        self.assertTrue(req_low['gm'])
        self.assertFalse(req_low['md'])
        
        # Evaluate for 100,000
        req_high = rule_model._get_required_approvals('allocation', 100000.0)
        self.assertTrue(req_high['gm'])
        self.assertTrue(req_high['md'])
