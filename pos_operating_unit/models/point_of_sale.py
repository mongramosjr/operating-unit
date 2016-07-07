# -*- coding: utf-8 -*-
##############################################################################
#
#    POS with Operating Units
#   
#    Copyright © 2016 Basement720 Technology, Inc.
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of POS with Operating Units and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

import logging
from openerp import api, fields, models, _   

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    
    @api.model
    def add_payment(self, order_id, data):
        statement_id = super(PosOrder, self).add_payment(order_id, data)
        
        _logger.warning('MONG %s', data)
        
        return statement_id
        
    @api.model
    def _create_account_move(self, dt, ref, journal_id, company_id):
        move_id = super(PosOrder, self)._create_account_move(dt, ref, journal_id, company_id)
        account_move = self.env['account.move'].browse(move_id)
        
        domain = [('sale_journal', '=', journal_id)]
        pos_order = self.env['pos.order'].search(domain, limit=1)
        
        if account_move and pos_order:
            account_move.operating_unit_id = pos_order.location_id.operating_unit_id
        
        return move_id
    
    @api.multi
    def action_invoice(self):
        result = super(PosOrder, self).action_invoice()
        for pos_order in self:
            operating_unit_id = pos_order.location_id.operating_unit_id
            pos_order.invoice_id.operating_unit_id = operating_unit_id
        
        return result


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'
    
    def _prepare_reconciliation_move(self, move_name):

        result = super(AccountBankStatementLine, self)._prepare_reconciliation_move(move_name)
        
        if self.pos_statement_id:
            result['operating_unit_id'] =  self.pos_statement_id.location_id.operating_unit_id.id
        return result
        
    def _prepare_reconciliation_move_line(self, move, amount):
        
        result = super(AccountBankStatementLine, self)._prepare_reconciliation_move_line(move, amount)
        
        if self.pos_statement_id:
            result['operating_unit_id'] =  self.pos_statement_id.location_id.operating_unit_id.id
        
        return result
