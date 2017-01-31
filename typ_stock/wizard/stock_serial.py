# coding: utf-8

from lxml import etree
import simplejson
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


def domain_str_append(old_domain_str, subdomain_str):
    if old_domain_str:
        return old_domain_str.replace(
            "]",
            ", " + subdomain_str + "]")
    return "[" + subdomain_str + "]"


def apply_modifiers(node, dict_modifiers):
    modifiers = {}
    if node.get('modifiers'):
        modifiers = simplejson.loads(node.get('modifiers'))
    for key in dict_modifiers.keys():
        modifiers[key] = dict_modifiers[key]
    node.set('modifiers', simplejson.dumps(modifiers))
    return node


class StockSerial(models.TransientModel):

    _inherit = 'stock.serial'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """Allows consult lot by lot_id field when picking is created from a
        sale order"""

        res = super(StockSerial, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        context = self._context
        if 'serial_ids' in res['fields']:
            arch = res['fields']['serial_ids'][
                'views']['tree']['arch']
            doc = etree.XML(arch)
            if context.get('active_model') == 'stock.move' \
               and context.get('active_id'):
                move = self.env['stock.move'].\
                    browse(context['active_id'])
                for node in doc.xpath("//field[@name='serial']"):
                    if move.picking_type_id.use_existing_lots:
                        node = apply_modifiers(node, {'readonly': True})
                    else:
                        node = apply_modifiers(node, {'required': True})
                for node in doc.xpath("//field[@name='lot_id']"):
                    sub_domain = False
                    if move.picking_type_id.use_existing_lots:
                        node = apply_modifiers(node, {'required': True})
                        node.set('options',
                                 "{'no_create': True}")
                        # Set domain to show only serial number
                        # that exists in source location
                        sub_domain = "('product_id', '=?', " + "product_id)," \
                            " ('last_location_id', '=', " + "source_loc_id)"
                    else:
                        node = apply_modifiers(node, {'readonly': True})

                    if sub_domain:
                        new_domain = domain_str_append(
                            node.get('domain'), sub_domain)
                        node.set('domain', new_domain)
                res['fields']['serial_ids']['views'][
                    'tree']['arch'] = etree.tostring(doc)
        return res

    @api.model
    def default_get(self, field_list):
        res = super(StockSerial, self).default_get(field_list)
        move_obj = self.env['stock.move']
        move_ids = self._context.get('active_id', [])
        move_id = move_obj.browse(move_ids)
        product_id = move_id.product_id.id
        res['product_qty'] = sum(
            move_id.picking_id.move_lines.
            filtered(lambda mov: mov.product_id.id == product_id).
            mapped('product_uom_qty'))
        return res

    @api.onchange('serial_ids')
    def onchange_serial(self):
        move = self.env['stock.move'].browse(self._context['active_id'])
        if move.picking_type_id.use_existing_lots:
            serial = []
            for serial_id in self.serial_ids:
                if serial_id.lot_id in serial:
                    return {
                        'warning': {
                            'title': _('Warning'),
                            'message': (
                                _('The Serial number %s already captured') %
                                (serial_id.lot_id.name.encode('utf-8')))
                        }}
                else:
                    serial.append(serial_id.lot_id)

        else:
            return super(StockSerial, self).onchange_serial()

    @api.multi
    def move_serial(self):
        quant_obj = self.env['stock.quant']

        for move in self:
            move_id = move.move_id
            product_id = move_id.product_id.id
            move_id.picking_id.pack_operation_ids.filtered(
                lambda dat: dat.product_id.id == product_id).unlink()

            total_product_uom_qty = sum(
                move_id.picking_id.move_lines.
                filtered(lambda mov: mov.product_id.id == product_id).
                mapped('product_uom_qty'))

            if len(move.serial_ids) > total_product_uom_qty:
                raise ValidationError(
                    _('The serial numbers loaded cannot be greater'
                      ' than the requested quantity of the product'))

            if move_id.picking_type_id.use_existing_lots:
                move_id.do_unreserve()

            for move_serial in move.serial_ids:
                # This validation by picking type code and
                # picking type create/existing lots is necessary because
                # the lot can be used again if are not present in someone
                # location of type internal and not need to be created
                if move_id.picking_type_id.use_create_lots:
                    if quant_obj.search_count(
                        [('product_id', '=', move_id.product_id.id),
                         ('lot_id.name', '=', move_serial.serial),
                         ('qty', '>', 0.0),
                         ('location_id.usage', '=', 'internal')]):
                        raise ValidationError(
                            _('The serial number %s is already stock') %
                            (move_serial.serial))
                    self._get_pack_ops_lot(move, move_serial)
                elif all(
                    [move_id.picking_type_id.use_existing_lots,
                     move_id.picking_id.picking_type_id.code == 'incoming']):
                    if quant_obj.search_count(
                        [('product_id', '=', move_id.product_id.id),
                         ('lot_id', '=', move_serial.lot_id.id),
                         ('qty', '>', 0.0),
                         ('location_id.usage', '=', 'internal')]):
                        raise ValidationError(
                            _('The serial number %s is already stock') % (
                                move_serial.serial))
                    self._get_pack_ops_lot(move, move_serial)
                elif not move_serial.lot_id:
                    raise ValidationError(
                        _('Serial number %s not found') % (move_serial.serial))
                elif move_serial.lot_id.quant_ids.filtered('reservation_id'):
                    raise ValidationError(
                        _('The serial number %s is already reserved in'
                          ' another move') % (move_serial.serial))
                else:
                    quants = quant_obj.quants_get_prefered_domain(
                        move_id.location_id,
                        move_id.product_id,
                        qty=1,
                        domain=[],
                        prefered_domain_list=[],
                        restrict_lot_id=move_serial.lot_id.id,
                        restrict_partner_id=[],
                    )
                    quant_obj.quants_reserve(quants, move_id)
        return True


class StockSerialLine(models.TransientModel):

    _inherit = 'stock.serial.line'

    def _compute_default_partner_id(self):
        move = 'move_id' in self._context and \
            self.env['stock.move'].browse(self._context['move_id']) or False
        return move and move.product_id or False

    def _compute_default_location_id(self):
        move = 'move_id' in self._context and \
            self.env['stock.move'].browse(self._context['move_id']) or False
        return move and move.location_id or False

    product_id = fields.Many2one('product.product',
                                 default=_compute_default_partner_id)
    source_loc_id = fields.Many2one('stock.location',
                                    default=_compute_default_location_id)
    serial = fields.Char('Serial', required=False)

    @api.onchange('serial', 'lot_id')
    def onchange_lot_id(self):
        move_obj = self.env['stock.move']
        move = self._context.get('move_id', [])
        move_id = move_obj.browse(move)
        quant_obj = self.env['stock.quant']

        super(StockSerialLine, self).onchange_lot_id()
        if self.lot_id:
            serial_number = self.lot_id.name.encode('utf-8')
            if move_id.picking_id.picking_type_id.code == 'incoming':
                other_quants = quant_obj.search(
                    [('product_id', '=', move_id.product_id.id),
                     ('lot_id', '=', self.lot_id.id),
                     ('qty', '>', 0.0),
                     ('location_id.usage', '=', 'internal')])
                if other_quants:
                    return {
                        'warning': {
                            'title': _('Warning'),
                            'message': (
                                _('The serial number %s is already in stock')
                                % (serial_number))
                        }}
            self.serial = serial_number
