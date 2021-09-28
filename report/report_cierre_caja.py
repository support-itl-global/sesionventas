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
        for factura in o.facturas_ids:
            if factura.state == 'paid' and factura.type != 'out_refund':
                facturas += factura.amount_total_signed
            if factura.state == 'cancel' and factura.type != 'out_refund':
                facturas_anuladas += factura.amount_total_signed
            if factura.state == 'open' and factura.type != 'out_refund':
                facturas_credito += factura.amount_total
        for factura in o.facturas_ids:
            if factura.state in ['open','paid'] and factura.type == 'out_refund':
                notas_credito += factura.amount_total
            if factura.state == 'cancel' and factura.type == 'out_refund':
                notas_credito_anuldas += factura.amount_total
        return {'facturas': facturas,'notas_credito': notas_credito,'notas_credito_anuladas': notas_credito_anuldas,'facturas_anuladas': facturas_anuladas,'facturas_credito': facturas_credito}

    def a_letras(self,monto):
        return a_letras.num_a_letras(monto)

    def _datos_ingresos(self,o):
        pagos = {}
        pago_credito = 0
        total_ingreso_dia = 0
        total_caja = 0
        anticipo = 0
        for pago in o.pagos_ids:
            if pago.reconciled_invoice_ids == False:
                anticipo += pago.amount
        for pago in o.pagos_ids:
            for factura in pago.reconciled_invoice_ids:
                if factura.sesion_ventas_id.id != o.id:
                    pago_credito += pago.amount
                else:
                    pagos[pago.id] = {
                        'journal_id': pago.journal_id.name,
                        'monto': pago.amount,
                    }
        llave = 'journal_id'
        pagos_agrupados = {}
        for pago in pagos.values():
            if pago[llave] not in pagos_agrupados:
                pagos_agrupados[pago[llave]] = {'diario': pago['journal_id'], 'monto': 0}
            pagos_agrupados[pago[llave]]['monto'] += pago['monto']
            total_ingreso_dia += pago['monto']
        total_caja = total_ingreso_dia + pago_credito + anticipo
        pagos_agrupados = pagos_agrupados.values()
        return {'pago_credito': pago_credito,'anticipo':anticipo,'pagos_agrupados':pagos_agrupados,'total_ingreso_dia': total_ingreso_dia,'total_caja': total_caja}

    def facturas_pagos(self,o):
        facturas = []
        pagos = []
        ventas_lista = []
        pagos_lista = []
        ventas = self.env['sale.order'].search([['sesion_ventas_id', '=', o.id]])
        for venta in ventas:
            ventas_lista.append(venta.name)
        facturas_ids = self.env['account.invoice'].search([('origin', 'not in', ventas_lista),('date_invoice','=',o.fecha)])
        if facturas_ids:
            for factura in facturas_ids:
                if factura.payment_ids:
                    for pago in factura.payment_ids:
                        pagos_lista.append(pago.id)
                facturas.append({
                    'fecha': factura.date_invoice,
                    'cliente': factura.partner_id.name,
                    'numero': factura.number,
                    'origen': factura.origin,
                    'ref_pago': factura.reference,
                    'total': factura.amount_total,
                    'estado': factura.state,
                })
        pagos_ids = self.env['account.payment'].search([('id', 'not in', pagos_lista),('payment_date','=',o.fecha)])
        if pagos_ids:
            for pago in pagos_ids:
                pagos.append({
                    'fecha': pago.payment_date,
                    'cliente': pago.partner_id.name,
                    'numero_pago': pago.name,
                    'origen': pago.communication,
                    'diario': pago.journal_id.name,
                    'total': pago.amount,
                    'estado': pago.state,
                })

        return {'facturas_ids': facturas, 'pagos_ids': pagos}

    @api.model
    def _get_report_values(self, docids, data=None):
        model = 'sesion.ventas'
        docs = self.env['sesion.ventas'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'a_letras': self.a_letras,
            '_datos_ventas': self._datos_ventas,
            '_datos_ingresos': self._datos_ingresos,
            'facturas_pagos': self.facturas_pagos,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
