# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    buffer_count = fields.Integer(compute="_compute_buffer_count")

    def _compute_buffer_count(self):
        for rec in self:
            rec.buffer_count = sum(
                variant.buffer_count for variant in rec.product_variant_ids
            )

    def action_view_stock_buffers(self):
        return self.product_variant_ids.action_view_stock_buffers()
