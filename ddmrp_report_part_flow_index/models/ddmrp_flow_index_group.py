# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class DdmrpFlowIndexGroup(models.Model):
    _name = "ddmrp.flow.index.group"
    _order = "sequence, id"
    _description = "DDMRP Flow Index Group"

    name = fields.Char(required=True)
    summary = fields.Text()
    active = fields.Boolean(default=True)
    lower_range = fields.Float(help="Lower range used to assign in stock buffer")
    upper_range = fields.Float(help="Upper range used to assign in stock buffer")
    sequence = fields.Integer(required=True)

    def _match(self, value):
        """Return the first group (by sequence) in ``self`` whose range contains
        ``value``. ``self`` is expected to be pre-ordered by sequence. An unset
        bound (0.0) is treated as open-ended on that side."""
        for group in self:
            lower, upper = group.lower_range, group.upper_range
            if lower and upper:
                if lower <= value <= upper:
                    return group
            elif upper:
                if value <= upper:
                    return group
            elif lower:
                if value >= lower:
                    return group
        return self.browse()
