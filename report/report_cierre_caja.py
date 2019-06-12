# -*- encoding: utf-8 -*-

from odoo import api, models, fields
import odoo.addons.l10n_gt_extra.a_letras as a_letras
import re
import logging

class ReportCierreCaja(models.AbstractModel):
    _name = 'report.sesionventas.report_cierre_caja'

    def _datos_ventas(self,o):
        facturas = 0
        facturas_anuladas = 0
        notas_credito = 0
        notas_credito_anuldas = 0
        facturas_credito = 0
        facturas_ids = self.env['account.invoice'].search([('sesion_ventas_id','=',o.id)])
        for factura in o.facturas_ids:
            if factura.state == 'paid':
                facturas += factura.amount_total_signed
            if factura.state == 'cancel':
                facturas_anuladas += factura.amount_total_signed
            if factura.state == 'open':
                facturas_credito += factura.amount_total
        for factura in facturas_ids:
            if (factura.state == 'open' or factura.state == 'paid') and type == 'out_refund':
                notas_credito += factura.amount_total
            if factura.state == 'cancel' and factura.type == 'out_refund':
                notas_credito_anuldas += factura.amount_total
        return {'facturas': facturas,'notas_credito': notas_credito,'notas_credito_anuladas': notas_credito_anuldas,'facturas_anuladas': facturas_anuladas,'facturas_credito': facturas_credito}


    def _datos_ingresos(self,o):
        pagos = {}
        pago_credito = 0
        total_ingreso_dia = 0
        total_caja = 0
        for pago in o.pagos_ids:
            for factura in pago.invoice_ids:
                if factura.sesion_ventas_id.id != o.id:
                    pago_credito += pago.amount
                else:
                    pagos[pago.id] = {
                        'journal_id': pago.journal_id.name,
                        'monto': pago.amount,
                    }
        logging.warn(pagos)
        llave = 'journal_id'
        pagos_agrupados = {}
        for pago in pagos.values():
            if pago[llave] not in pagos_agrupados:
                pagos_agrupados[pago[llave]] = {'diario': pago['journal_id'], 'monto': 0}
            pagos_agrupados[pago[llave]]['monto'] += pago['monto']
            total_ingreso_dia += pago['monto']
        total_caja = total_ingreso_dia + pago_credito
        pagos_agrupados = pagos_agrupados.values()
        return {'pago_credito': pago_credito,'pagos_agrupados':pagos_agrupados,'total_ingreso_dia': total_ingreso_dia,'total_caja': total_caja}

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = 'sesion.ventas'
        docs = self.env[self.model].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'a_letras': a_letras,
            '_datos_ventas': self._datos_ventas,
            '_datos_ingresos': self._datos_ingresos,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
