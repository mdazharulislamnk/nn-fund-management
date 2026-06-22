# -*- coding: utf-8 -*-
{
    'name': 'NN Fund Management',
    'version': '1.0',
    'summary': 'Strict Fund Management, Allocation, Requisition, and Approval Workflow',
    'description': """
NN Fund Management
==================
A strict and secure module designed to manage incoming funds, unassigned balances, project and expense head allocations, fund requisitions, bills against approved requisitions, and internal transfers.

Features Include:
- Strict double-spending prevention dynamically managed via computed holds.
- Multi-company data isolation.
- Structured State Machine Workflow for strict GM -> MD Approvals.
- Full audit tracking for all financial operations.
- Non-editable calculated balances.
    """,
    'author': 'Your Name/NN Services',
    'website': 'https://github.com/mdazharulislamnk/nn-fund-management',
    'category': 'Accounting/Localizations',
    'depends': ['base', 'account', 'board', 'mail'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/fund_account_views.xml',
        'views/project_expense_head_views.xml',
        'views/fund_allocation_views.xml',
        'views/fund_requisition_views.xml',
        'views/fund_transfer_views.xml',
        'views/account_move_views.xml',
        'views/audit_history_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
