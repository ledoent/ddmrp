# Copyright 2025 Ledo Enterprises LLC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "DDMRP Spreadsheet",
    "summary": "Spreadsheet dashboards for DDMRP buffer monitoring",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Beta",
    "author": "Ledo Enterprises LLC, Odoo Community Association (OCA)",
    "maintainers": ["dnplkndll"],
    "website": "https://github.com/OCA/ddmrp",
    "category": "Warehouse",
    "depends": [
        "ddmrp",
        "ddmrp_history",
        "spreadsheet_oca",
    ],
    "data": [
        "views/stock_buffer_views.xml",
    ],
    "demo": [
        "demo/spreadsheet_spreadsheet.xml",
    ],
    "installable": True,
}
