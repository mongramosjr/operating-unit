# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.constrains('operating_unit_id', 'warehouse_id')
    def _check_wh_operating_unit(self):
        if self.operating_unit_id and\
                self.operating_unit_id != self.warehouse_id.operating_unit_id:
            raise UserError(_('Configuration error!\nThe Operating Unit \
            in the Sales Order and in the Warehouse must be the same.'))
            
    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id and self.warehouse_id.operating_unit_id:
            self.operating_unit_id = self.warehouse_id.operating_unit_id.id
        if self.warehouse_id.company_id:
            self.company_id = self.warehouse_id.company_id.id
        super(SaleOrder, self)._onchange_warehouse_id()
        

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _prepare_picking_assign(self, move):
        """
        Override to add Operating Units to Picking.
        """
        values = super(StockMove, self)._prepare_picking_assign(move)
        sale_line = move.procurement_id and move.procurement_id.sale_line_id
        if sale_line:
            values.update({
                'operating_unit_id': sale_line.order_id and
                sale_line.order_id.operating_unit_id.id
            })
        return values
