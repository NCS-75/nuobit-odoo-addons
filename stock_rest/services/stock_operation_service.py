# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError


class OperationService(Component):
    _inherit = "stock.service"
    _name = "operation.service"
    _usage = "operations"
    _description = """
        Operation Services
        Create stock operations
    """

    def create(self, **kwargs):
        # validate client call
        company_id = self.env['res.users'].search([
            ('id', '=', self.env.uid),
        ]).company_id.id

        picking_type_id = self.env['stock.picking.type'].search([
            ('name', '=', 'Internal Transfers'),
        ], order='id asc', limit=1)

        # Setting Source and destination
        src_location_id = self.env['stock.location'].search([
            ('company_id', '=', company_id),
            ('code', '=', kwargs['source']),
        ])

        dst_location_id = self.env['stock.location'].search([
            ('company_id', '=', company_id),
            ('code', '=', kwargs['destination']),
        ])
        # employees
        employees = None
        if kwargs['employees']:
            sage_company_id = self.env['sage.backend'].sudo().search([
                ('company_id', '=', company_id),
            ]).sage_company_id
            employees = self.env['sage.hr.employee'].sudo().search([
                ('company_id', '=', company_id),
                ('sage_codigo_empresa', '=', sage_company_id),
                ('sage_codigo_empleado', 'in', kwargs['employees']),
            ])
            employee_diff = set(kwargs['employees']) - set(employees.mapped('sage_codigo_empleado'))
            if employee_diff:
                raise ValidationError("Employees %s are not found" % employee_diff)

        # group by product
        moves_by_product = {}
        for product_line in kwargs['products']:
            moves_by_product.setdefault(product_line['id'], []).append(product_line)

        # Picking
        picking_values = {
            'picking_type_id': picking_type_id.id,
            'location_id': src_location_id.id,
            'location_dest_id': dst_location_id.id,
            'partner_ref': kwargs['service_num'],
        }

        if employees:
            picking_values.update({
                'employee_ids': [(6, False, employees.mapped('odoo_id.id'))],
            })

        ## Create moves
        moves = []
        for product_id in moves_by_product.keys():
            obj = self.env['product.product'].browse(product_id)
            if obj.sudo().asset_category_id and not kwargs['asset']:
                raise ValidationError("You cannot consume an asset. %s [%s]. "
                                      "Add the parameter 'asset=true' to the call to force it" % (
                                          obj.id, obj.default_code))
            moves.append({
                'product_id': obj.id,
                'product_uom': obj.uom_id.id,
                'name': obj.display_name,
                'picking_type_id': picking_type_id.id,
                'origin': False, })
        if moves:
            picking_values.update({
                'move_lines': [(0, False, v) for v in moves],
            })

        # create picking
        picking_id = self.env['stock.picking'].create(picking_values)

        # Create move_lines
        for move in picking_id.move_lines:
            product_id = move.product_id
            uom_id = move.product_uom
            move_lines = []
            for ml in moves_by_product[product_id.id]:
                move_line = {
                    'product_id': product_id.id,
                    'location_id': src_location_id.id,
                    'location_dest_id': dst_location_id.id,
                    'qty_done': ml['quantity'],
                    'product_uom_id': uom_id.id,
                    'picking_id': picking_id.id,
                }
                if 'lot_id' in ml:
                    move_line.update({
                        'lot_id': ml['lot_id']
                    })
            move_lines.append(move_line)
            move.move_line_ids = [(0, False, v) for v in move_lines]

        # Validate Picking
        if kwargs['validate']:
            picking_id.button_validate()
        return {'picking_id': picking_id.id}

    def _validator_create(self):
        res = {
            "source": {"type": "string", "required": True, "empty": False},
            "destination": {"type": "string", "required": True, "empty": False},
            "validate": {"type": "boolean", "default": True},
            "asset": {"type": "boolean", "default": False},
            "products": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "required": True,
                    "schema": {
                        "id": {"type": "integer", "required": True},
                        "quantity": {"type": ("integer", "float"), "required": True},
                        "lot_id": {"type": "integer", "required": True},
                    },
                },
            },
            "service_num": {"type": "string", "required": True},
            "employees": {
                "type": "list",
                "default": [],
                "schema": {"type": "integer", "required": True, "nullable": True}
            },
        }
        return res

    def _validator_return_create(self):
        return_get = {"picking_id": {"type": "integer", "required": True}}
        return return_get
