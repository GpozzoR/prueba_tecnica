{
    "name": "Reporte de salida y entrada de productos",
    "summary":""""
        El modal de los reportes se encuentra ubicado en la el menu de informes de inventario
    """,
    "license": "LGPL-3",
    "version": "16.0.0.1.0",
    "depends": ["stock","sale", 
                "purchase","product", "report_xlsx" ],
    "data": [
        # Data
        #security
        "security/ir.model.access.csv",
        # Wizards
        "wizard/in_out_product_wizard.xml",
        # Reports
        "reports/report_in_out_products.xml",
    ],

}
