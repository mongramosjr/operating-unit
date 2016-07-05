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

from openerp import fields, models


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'
    
    operating_unit_ids = fields.Many2many('operating.unit',
                                          string='Operating Units',
                                          required=False)

    def _build_contexts(self, data):
        result = super(AccountBalanceReport, self)._build_contexts(data)
        data2 = {}
        data2['form'] = self.read(['operating_unit_ids'])[0]
        result['operating_unit_ids'] = 'operating_unit_ids' in data2['form']\
                                       and data2['form']['operating_unit_ids']\
                                       or False
        return result
