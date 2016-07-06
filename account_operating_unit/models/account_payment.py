# -*- coding: utf-8 -*-
##############################################################################
#
#    Accounting with Operating Units
#   
#    Copyright © 2016 Basement720 Technology, Inc.
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Accounting with Operating Units and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"
    
    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        help="This operating unit will "
                                             "be defaulted in the move.")
    @api.model
    def default_get(self, fields):
        result = super(account_register_payments, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        invoices = self.env[active_model].browse(active_ids)
        result['operating_unit_id'] = invoices[0].operating_unit_id.id
        return result
    
    def get_payment_vals(self):
		
		result = super(AccountRegisterPayments, self).get_payment_vals()
		
		result['operating_unit_id']=self.operating_unit_id.id
		
		return result



class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        help="This operating unit will "
                                             "be defaulted in the move.")

    
    @api.model
    def default_get(self,fields):
        result = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', result.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            result['operating_unit_id'] = invoice['operating_unit_id'][0]
        return result
        
    def _get_move_vals(self, journal=None):
        result =  super(AccountPayment, self)._get_move_vals(journal)
        result['operating_unit_id'] = self.operating_unit_id.id
        return result
        
    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        result =  super(AccountPayment, self)._get_shared_move_line_vals(debit, credit, amount_currency, move_id, invoice_id)
        result['operating_unit_id'] = self.operating_unit_id.id
        return result
    
    def _get_counterpart_move_line_vals(self, invoice=False):
        result =  super(AccountPayment, self)._get_counterpart_move_line_vals(invoice)
        result['operating_unit_id'] = self.operating_unit_id.id
        return result
        
    def _get_liquidity_move_line_vals(self, amount):
        result =  super(AccountPayment, self)._get_liquidity_move_line_vals(amount)
        result['operating_unit_id'] = self.operating_unit_id.id
        return result
