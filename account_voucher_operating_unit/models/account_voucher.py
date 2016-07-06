# -*- coding: utf-8 -*-
##############################################################################
#
#    Accounting with Operating Units
#   
#    Copyright © 2016 Basement720 Technology, Inc.
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Accounting with Operating Units and is released under
#    the BSD-3.0 License: http://www.opensource.org/licenses/bsd-license.php
##############################################################################

from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    @api.model
    def _get_default_operating_unit(self):
        journal = self._default_journal()
        voucher_type = self._context.get('voucher_type', False)
        if voucher_type in ('sale', 'purchase'):
            if journal.default_debit_account_id.operating_unit_id:
                return journal.default_debit_account_id.operating_unit_id
        else:
            if journal.default_credit_account_id.operating_unit_id:
                return journal.default_credit_account_id.operating_unit_id
        
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', default=_get_default_operating_unit)
    

    @api.one
    @api.constrains('operating_unit_id', 'company_id')
    def _check_company_operating_unit(self):
        if self.company_id and self.operating_unit_id and \
                self.company_id != self.operating_unit_id.company_id:
            raise UserError(_('The Operating Unit must belong to the company in the voucher and in the '))

    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        result = super(AccountVoucher, self).first_move_line_get(move_id, company_currency, current_currency)
        
        #force to use the OU of account
        if not self.operating_unit_id:
            if self.account_id.operating_unit_id:
                result['operating_unit_id'] = self.account_id.operating_unit_id.id
            else:
                raise UserError(_('Account %s - %s does not have a default operating unit.') % (self.account_id.code, self.account_id.name))
            
        if self.voucher_type in ('sale', 'purchase'):
            if self.operating_unit_id:
                result['operating_unit_id'] = self.operating_unit_id.id
            elif self.account_id.operating_unit_id:
                result['operating_unit_id'] = self.account_id.operating_unit_id.id
            else:
                raise UserError(_('Account %s - %s does not have a default operating unit. \n '
                                'Default debit and credit account in the journal % should have a default Operating Unit.') %
                              (self.account_id.code, self.account_id.name, self.journal_id.name))
        else:
            if self.operating_unit_id:
                result['operating_unit_id'] = self.operating_unit_id.id
            elif self.account_id.operating_unit_id:
                result['operating_unit_id'] = self.account_id.operating_unit_id.id
            else:
                raise UserError(_('The Voucher must have an Operating Unit.'))
        return result
    
    #OU in account.move will be defaulted in the move lines
    @api.multi
    def account_move_get(self):
        
        result = super(AccountVoucher, self).account_move_get()
        
        if self.operating_unit_id:
            result['operating_unit_id'] = self.operating_unit_id.id
        elif self.account_id.operating_unit_id:
            result['operating_unit_id'] = self.account_id.operating_unit_id.id
        
        return result


class AccountVoucherLine(models.Model):
    _inherit = "account.voucher.line"

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', related='voucher_id.operating_unit_id', readonly=True, store=True)
