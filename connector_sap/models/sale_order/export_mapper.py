# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, only_create)
from odoo.exceptions import ValidationError


class SaleOrderExportMapChild(Component):
    _name = 'sap.sale.order.map.child.export'
    _inherit = 'sap.map.child.export'

    _apply_on = 'sap.sale.order.line'

    def get_item_values(self, map_record, to_attr, options):
        return super().get_item_values(map_record, to_attr, options)
        # binder = self.binder_for('sap.sale.order.line')
        # external_id = map_record.source['id']
        # sap_order_line = binder.to_internal(external_id, unwrap=False)
        # if sap_order_line:
        #     map_record.update(id=sap_order_line.id)
        # return map_record.values(**options)

    def format_items(self, items_values):
        return super().format_items(items_values)
        # ops = []
        # for values in items_values:
        #     id = values.pop('id', None)
        #     if id:
        #         ops.append((1, id, values))
        #     else:
        #         ops.append((0, False, values))
        # return ops


class SaleOrderExportMapper(Component):
    _name = 'sap.sale.order.export.mapper'
    _inherit = 'sap.export.mapper'

    _apply_on = 'sap.sale.order'

    direct = []

    children = [('order_line', 'DocumentLines', 'sap.sale.order.line')]

    @mapping
    def partner(self, record):
        parent = record.partner_shipping_id.parent_id
        if not parent:
            raise ValidationError(_('No parent partner found for partner %s') % record.name)
        partner_map = self.backend_record.partner_ids.filtered(lambda x: x.partner_id == parent)
        if not partner_map:
            raise ValidationError(_('No partner mapping found for parent %s') % parent.name)
        return {'CardCode': partner_map.sap_cardcode}

    @mapping
    def date(self, record):
        return {'DocDueDate': fields.Date.from_string(record.date_order)}

    @mapping
    def shiptocode(self, record):
        binder = self.binder_for('sap.res.partner')
        binding = binder.wrap_record(record.partner_shipping_id)
        assert binding, (
                "partner %s should have been exported in "
                "SaleOrderExporter._export_dependencies" % record.partner_shipping_id)
        return {'ShipToCode': binding.sap_addressname}
