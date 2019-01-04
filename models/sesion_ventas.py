# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError
from datetime import datetime
import logging

class SesionVenas(models.Model):
    _name = "sesion.ventas"
    _rec_name = "nombre"

    def _compute_facturas_ids(self):
        ventas_lista = []
        ventas = self.env['sale.order'].search([['sesion_ventas_id', '=', self.id]])
        for venta in ventas:
            ventas_lista.append(venta.name)
        facturas = self.env['account.invoice'].search([['origin', 'in', ventas_lista]]).ids
        self.facturas_ids = [(6, 0, facturas)]

    def _compute_pagos_ids(self):
        ventas_lista = []
        ventas = self.env['sale.order'].search([['sesion_ventas_id', '=', self.id]])
        for venta in ventas:
            ventas_lista.append(venta.name)
        pagos = self.env['account.payment'].search([['communication', 'in', ventas_lista]]).ids
        self.pagos_ids = [(6, 0, pagos)]

    nombre = fields.Char('Sesión',default=lambda self: _('Nuevo'))
    fecha = fields.Date("Fecha",default=datetime.today())
    responsable_id = fields.Many2one("res.users","Responsable",default=lambda self: self.env.user)
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('abierto', 'Abierto'),
        ('cerrado', 'cerrado'),
        ], string='Estado', readonly=True, copy=False, index=True, track_visibility='onchange', default='borrador')
    facturas_ids = fields.Many2many("account.invoice","sesion_ventas_facturas_rel",string="Facturas",compute='_compute_facturas_ids')
    pagos_ids = fields.Many2many("account.payment","sesion_ventas_pagos_rel",string="Pagos",compute='_compute_pagos_ids')
    diario_id = fields.Many2one("account.journal","Diario")
    usuarios_ids = fields.Many2many("res.users",'sesion_ventas_usuarios',string='Usuarios')

    @api.multi
    def action_abrir_sesion(self):
        for sesion in self:
            values = {}
            values['estado'] = 'abierto'
            sesion.write(values)
        return True

    @api.multi
    def action_cerrar_sesion(self):
        for sesion in self:
            values = {}
            values['estado'] = 'cerrado'
            sesion.write(values)
        return True

    @api.multi
    def unlink(self):
        for sesion in self:
            if not sesion.estado == 'borrador':
                raise UserError(_('No puede eliminar sesion'))
        return super(SesionVenas, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('nombre', _('Nuevo')) == _('Nuevo'):
            vals['nombre'] = self.env['ir.sequence'].next_by_code('sesion.ventas') or _('New')
        result = super(SesionVenas, self).create(vals)
        return result
