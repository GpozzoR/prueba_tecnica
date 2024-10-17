import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError



class ReportOutInProductsXlsx(models.AbstractModel):
    _name = 'report.out_in_products_report.report_in_out_products_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    def search_lines(self, ids, dates):
        query = f"""SELECT  p.id, s.qty_done ,s.reference, s.date
            FROM product_product p
            INNER JOIN stock_move_line s 
            ON p.id=s.product_id
            WHERE p.id {f"IN {tuple(ids)}" if len(ids) > 1 else f"= {ids[0]}"} AND s.state = 'done' AND s.date {f">= '{str(dates[0])}'" if not dates[1] else f"BETWEEN '{str(dates[0])}' AND '{str(dates[1])}'"}
            ORDER BY s.date ASC
            """
        self.env.cr.execute(query)
        dic = self.env.cr.dictfetchall()
        if not dic:
            raise ValidationError("No se ha encontrado movimientos relacionados")

        products = {pd.id:pd.display_name for pd in self.env['product.product'].browse([i['id'] for i in dic])}
        stock = []
        other = []
        sale = []
        purchase = []
        
        for move in dic:
            if ' ' in move['reference']:
                stock.append({'move':'Ajuste','reference': move['reference'], 'name':products.get(move['id']), 'date':f"{move['date']}",'qty':f"+{move['qty_done']}"})
            else:   
                other.append({'reference':move['reference'],'name':products.get(move['id']),'date':f"{move['date']}" ,'qty':move['qty_done']})
        
        if other:
            reference = [i['reference'] for i in other]
            query = f"""SELECT  origin, name
            FROM stock_picking
            WHERE name {f"IN {tuple(reference)}" if len(reference) > 1 else f"= '{reference[0]}'"} AND origin IS NOT NULL
            """
            self.env.cr.execute(query)
            dic = self.env.cr.dictfetchall()
            for move  in dic:
                if 'S' in  move['origin']:
                    reference = [{'move':'Venta','reference': f"{i['reference']} ({move['origin']})", 'name':i['name'], 'date':f"{i['date']}" ,'qty':f"-{i['qty']}"} for i in other if i['reference'] == move['name'] ]
                    sale.extend(reference)
                elif 'P' in  move['origin']:
                    reference = [{'move':'Compra','reference': f"{i['reference']} ({move['origin']})", 'name':i['name'],'date':f"{i['date']}" ,'qty':f"+{i['qty']}"} for i in other if i['reference'] == move['name'] ]
                    purchase.extend(reference)

        return stock, sale, purchase



    def generate_xlsx_report(self, workbook, data, partners):
        dates = data.get('dates')
        products = data.get('products')
        category = data.get('category')

        if category:
            query = f"""SELECT  default_code
            FROM product_template
            WHERE categ_id = {category} AND default_code IS NOT NULL
            """
            self.env.cr.execute(query)
            dic = self.env.cr.dictfetchall()

            query = f"""SELECT  id
            FROM product_product
            WHERE default_code IN {tuple([i['default_code']for i in dic])}
            """
            self.env.cr.execute(query)
            dic = self.env.cr.dictfetchall()

            # logging.info(dic)
            stock, sale, purchase = self.search_lines([i['id'] for i in dic], dates)
            # raise ValidationError(F"{stock}, {sale}, {purchase}")

        elif products:
            stock, sale, purchase = self.search_lines(products, dates)


            # raise ValidationError(f"{stock}, {sale}, {purchase}")

        report_name = 'Reporte de salidas y entradas'
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        cell_format = workbook.add_format({'bold': True,'bg_color': '#E9ECEF','text_wrap': True})
        lists = (['A','B','C','D','E'],['Nombre',
                                        'Fecha',
                                        'Tipo de Movimiento',
                                        'Referencia',
                                        'Cantidad '])
        for letters, tittles in zip(lists[0],lists[1]):
            sheet.set_column(f'{letters}:{letters}', 30)
            sheet.write(f'{letters}1',tittles, bold)


        row=1
        for title_type, type in zip(["Ajustes de inventario", "Ventas", "Compras"],[stock,sale,purchase]):
            for i in range(0,5):
                sheet.set_row(row, 30)
                sheet.write(row, 0, title_type, cell_format)
                sheet.write(row, i + 1, ' ' , cell_format)
            for line, num in zip(type, range(1,len(type)+1)):
                for line_info, line_num in zip([line['name'],line['date'],line['move'],line['reference'],line['qty']],range(0,6)):
                    sheet.write(row + num, line_num, line_info)
            row+= len(type) + 1
            
class ReportOutInProductsPdf(models.AbstractModel):
    _name = 'report.out_in_products_report.in_out_products_template'

    def search_lines(self, ids, dates):
        query = f"""SELECT  p.id, s.qty_done ,s.reference, s.date
            FROM product_product p
            INNER JOIN stock_move_line s 
            ON p.id=s.product_id
            WHERE p.id {f"IN {tuple(ids)}" if len(ids) > 1 else f"= {ids[0]}"} AND s.state = 'done' AND s.date {f">= '{str(dates[0])}'" if not dates[1] else f"BETWEEN '{str(dates[0])}' AND '{str(dates[1])}'"}
            ORDER BY s.date ASC
            """
        self.env.cr.execute(query)
        dic = self.env.cr.dictfetchall()
        if not dic:
            raise ValidationError("No se ha encontrado movimientos relacionados")

        products = {pd.id:pd.display_name for pd in self.env['product.product'].browse([i['id'] for i in dic])}
        stock = []
        other = []
        sale = []
        purchase = []
        
        for move in dic:
            if ' ' in move['reference']:
                stock.append({'move':'Ajuste','reference': move['reference'], 'name':products.get(move['id']), 'date':f"{move['date']}",'qty':f"+{move['qty_done']}"})
            else:   
                other.append({'reference':move['reference'],'name':products.get(move['id']),'date':f"{move['date']}" ,'qty':move['qty_done']})
        
        if other:
            reference = [i['reference'] for i in other]
            query = f"""SELECT  origin, name
            FROM stock_picking
            WHERE name {f"IN {tuple(reference)}" if len(reference) > 1 else f"= '{reference[0]}'"} AND origin IS NOT NULL
            """
            self.env.cr.execute(query)
            dic = self.env.cr.dictfetchall()
            for move  in dic:
                if 'S' in  move['origin']:
                    reference = [{'move':'Venta','reference': f"{i['reference']} ({move['origin']})", 'name':i['name'], 'date':f"{i['date']}" ,'qty':f"-{i['qty']}"} for i in other if i['reference'] == move['name'] ]
                    sale.extend(reference)
                elif 'P' in  move['origin']:
                    reference = [{'move':'Compra','reference': f"{i['reference']} ({move['origin']})", 'name':i['name'],'date':f"{i['date']}" ,'qty':f"+{i['qty']}"} for i in other if i['reference'] == move['name'] ]
                    purchase.extend(reference)

        return stock, sale, purchase


     # @api.model
    def _get_report_values(self, docids, data=None):
        dates = data.get('dates')
        products = data.get('products')
        category = data.get('category')

        if category:
            query = f"""SELECT  default_code
            FROM product_template
            WHERE categ_id = {category} AND default_code IS NOT NULL
            """
            self.env.cr.execute(query)
            dic = self.env.cr.dictfetchall()
            if not dic:
                raise ValidationError("No se ha encontrado movimientos relacionados")
                
            products = [i['default_code']for i in dic]

            query = f"""SELECT  id
            FROM product_product
            WHERE default_code {f"IN {tuple(products)}" if len(products) > 1 else f"= '{products[0]}'"}
            """
            self.env.cr.execute(query)
            dic = self.env.cr.dictfetchall()

            stock, sale, purchase = self.search_lines([i['id'] for i in dic], dates)

        elif products:
            stock, sale, purchase = self.search_lines(products, dates)

        return {
                'doc_ids': docids, 
                'doc_model': self.env['stock.move.line'], 
                'docs': [stock,sale,purchase] 
            }
   