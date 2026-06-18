# Copyright 2017-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo import api, fields, models

# Fallback observation window (working days) for the actual flow index when the
# buffer's ADU method defines no past horizon (e.g. fixed ADU).
DEFAULT_ACTUAL_HORIZON = 365


def _round_half_up(value):
    """Match PostgreSQL ``round()`` (half away from zero) for non-negative values,
    instead of Python's banker's rounding."""
    return int(value + 0.5)


class StockBuffer(models.Model):
    _inherit = "stock.buffer"

    # --- Planned flow index (derived from buffer sizing, kept up to date by the
    #     ORM whenever the green zone or ADU change) ---
    order_frequency = fields.Float(
        compute="_compute_order_frequency",
        store=True,
        digits="Product Unit of Measure",
        help="Planned order cycle, in days of ADU: Green Zone / ADU.",
    )
    order_frequency_group = fields.Integer(
        compute="_compute_order_frequency",
        store=True,
        help="Rounded planned order cycle, used to assign the Flow Index Group.",
    )
    flow_index_group_id = fields.Many2one(
        "ddmrp.flow.index.group",
        string="Flow Index Group",
        compute="_compute_flow_index_group_id",
        store=True,
        readonly=True,
    )

    # --- Actual flow index (derived from real replenishment history; refreshed by
    #     cron_actions, like the ADU) ---
    actual_order_count = fields.Integer(
        string="Actual Replenishments",
        readonly=True,
        help="Completed replenishments received over the observation window.",
    )
    actual_order_frequency = fields.Float(
        readonly=True,
        digits="Product Unit of Measure",
        help="Observed order cycle, in days: observation window / completed "
        "replenishments.",
    )
    actual_order_frequency_group = fields.Integer(readonly=True)
    actual_flow_index_group_id = fields.Many2one(
        "ddmrp.flow.index.group",
        string="Actual Flow Index Group",
        readonly=True,
    )

    def _flow_index_groups(self):
        """Flow index groups ordered by sequence, ready for range matching."""
        return self.env["ddmrp.flow.index.group"].search([], order="sequence, id")  # pylint: disable=no-search-all

    @api.depends("green_zone_qty", "adu")
    def _compute_order_frequency(self):
        for rec in self:
            freq = rec.green_zone_qty / rec.adu if rec.adu else 0.0
            rec.order_frequency = freq
            rec.order_frequency_group = _round_half_up(freq)

    @api.depends("order_frequency_group")
    def _compute_flow_index_group_id(self):
        groups = self._flow_index_groups()
        for rec in self:
            rec.flow_index_group_id = groups._match(rec.order_frequency_group)

    def _past_incoming_moves_domain(self, date_from, date_to, locations):
        """Completed replenishment moves into the buffer locations (the supply-side
        mirror of ``_past_moves_domain``)."""
        self.ensure_one()
        return [
            ("state", "=", "done"),
            ("location_dest_id", "in", locations.ids),
            ("location_id", "not in", locations.ids),
            ("product_id", "=", self.product_id.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]

    def _calc_actual_flow_index(self):
        groups = self._flow_index_groups()
        today = fields.Date.context_today(self)
        for rec in self:
            horizon = rec._get_horizon_adu_past_demand() or DEFAULT_ACTUAL_HORIZON
            date_to = today - timedelta(days=1)
            date_from = today - timedelta(days=horizon)
            locations = (
                rec.env["stock.location"]
                .with_context(active_test=False)
                .search([("id", "child_of", rec.location_id.ids)])
            )
            count = rec.env["stock.move"].search_count(
                rec._past_incoming_moves_domain(date_from, date_to, locations)
            )
            freq = (horizon / count) if count else 0.0
            group = _round_half_up(freq)
            rec.actual_order_count = count
            rec.actual_order_frequency = freq
            rec.actual_order_frequency_group = group
            rec.actual_flow_index_group_id = groups._match(group) if count else False

    def cron_actions(self, only_nfp=False):
        res = super().cron_actions(only_nfp=only_nfp)
        self._calc_actual_flow_index()
        return res
