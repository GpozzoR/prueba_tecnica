from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging



class InOutProductsWizard(models.TransientModel):
    _name = 'in.out.products.wizard'

    start = fields.Date(string='Fecha de inicio')
    end = fields.Date(string='Fecha final')
    categ_id = fields.Many2one('product.category', string='Categoría')
    product_ids = fields.Many2many('product.product', string='Productos')
    
    """
        Funcion para imprimir pdf
    """
    def _validation(self):
        if not self.categ_id and not self.product_ids:
            raise ValidationError("Al menos alguno de los campo de categoría o productos deben estar rellenos")

    def print_report_xlsx(self):
        self._validation()
        data = {
            'dates': [self.start, self.end],
            'category':self.categ_id.id,
            'products':self.product_ids.ids
        }
        return self.env.ref('out_in_products_report.report_in_out_products_xlsx_action').report_action(self, data=data)
    
    def print_report_pdf(self):
        self._validation()
        data = {
            'dates': [self.start, self.end],
            'category':self.categ_id.id,
            'products':self.product_ids.ids
        }
        return self.env.ref('out_in_products_report.report_in_out_products_pdf_action').report_action(self, data=data)
