# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError
from datetime import date
import logging

class SesionVentas(models.Model):
    _name = "sesion.ventas"
    _rec_name = "nombre"

    def _compute_facturas_ids(self):
        ventas_lista = []
        ventas = self.env['sale.order'].search([['sesion_ventas_id', '=', self.id]])
        facturas = []
        for venta in ventas:
            if venta.invoice_ids:
                for factura in venta.invoice_ids:
                    if factura.move_type == "out_invoice" and factura.state in ['draft','posted']:
                        facturas.append(factura.id)
        notas_credito = self.env['account.move'].search([('state','in',['draft','posted']),('move_type','=','out_refund'),('sesion_ventas_id','=',self.id)]).ids
        self.facturas_ids = [(6, 0, facturas+notas_credito)]

    def _compute_pagos_ids(self):
        ventas_lista = []
        pagos_lista = []
        pagos = self.env['account.payment'].search([('sesion_ventas_id','=',self.id)])
        for pago in pagos:
            # for factura in pago.reconciled_invoice_ids:
            if pago.sesion_ventas_id.id == self.id:
                # if factura.id in self.facturas_ids.ids or pago.sesion_ventas_id.id == self.id:
                pagos_lista.append(pago.id)
        self.pagos_ids = [(6, 0, pagos_lista)]

    nombre = fields.Char('Sesión',default=lambda self: _('Nuevo'))
    fecha = fields.Date("Fecha",default=date.today())
    responsable_id = fields.Many2one("res.users","Responsable",default=lambda self: self.env.user)
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('abierto', 'Abierto'),
        ('cerrado', 'cerrado'),
        ], string='Estado', readonly=True, copy=False, index=True, track_visibility='onchange', default='borrador')
    facturas_ids = fields.Many2many("account.move",string="Facturas",compute='_compute_facturas_ids')
    pagos_ids = fields.Many2many("account.payment",string="Pagos",compute='_compute_pagos_ids')
    diario_id = fields.Many2one("account.journal","Diario")
    usuarios_ids = fields.Many2many("res.users",string='Usuarios')

    def action_abrir_sesion(self):
        for sesion in self:
            values = {}
            values['estado'] = 'abierto'
            sesion.write(values)
        return True

    def action_cerrar_sesion(self):
        for sesion in self:
            values = {}
            values['estado'] = 'cerrado'
            sesion.write(values)
        return True

    def unlink(self):
        for sesion in self:
            if not sesion.estado == 'borrador':
                raise UserError(_('No puede eliminar sesion'))
        return super(SesionVentas, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('nombre', _('Nuevo')) == _('Nuevo'):
            vals['nombre'] = self.env['ir.sequence'].next_by_code('sesion.ventas') or _('New')
        result = super(SesionVentas, self).create(vals)
        return result
