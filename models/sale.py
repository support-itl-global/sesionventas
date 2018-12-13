
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _default_sesion(self):
        return self.env['sesion.ventas'].search([('estado', '=', 'abierto'), ('responsable_id', '=', self.env.uid)], limit=1)

    sesion_ventas_id = fields.Many2one("sesion.ventas",string="Session",domain="[('estado', '=', 'abierto')]",
        readonly=True, default=_default_sesion)
