# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestDDMRPReportPartFlowIndex(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.buffer_profile_mmm = self.env.ref(
            "ddmrp.stock_buffer_profile_replenish_manufactured_medium_medium"
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.adu_fixed = self.env.ref("ddmrp.adu_calculation_method_fixed")
        self.product = self.env["product.product"].create(
            {
                "name": "product test",
                "is_storable": True,
            }
        )
        self.buffer = self.env["stock.buffer"].create(
            {
                "buffer_profile_id": self.buffer_profile_mmm.id,
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "warehouse_id": self.warehouse.id,
                "adu_calculation_method": self.adu_fixed.id,
                "adu_fixed": 4.0,
                "order_cycle": 5,
            }
        )
        self.flow_index_group_1 = self.env["ddmrp.flow.index.group"].create(
            {"name": "Group 1", "lower_range": 1, "upper_range": 10, "sequence": 0}
        )
        self.flow_index_group_2 = self.env["ddmrp.flow.index.group"].create(
            {"name": "Group 2", "lower_range": 11, "upper_range": 30, "sequence": 1}
        )
        self.flow_index_group_3 = self.env["ddmrp.flow.index.group"].create(
            {"name": "Group 3", "lower_range": 31, "upper_range": 100000, "sequence": 2}
        )

    def _create_done_receipt(self, days_ago):
        """Create a completed replenishment move into the buffer location."""
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10.0,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "company_id": self.warehouse.company_id.id,
            }
        )
        date = fields.Datetime.now() - timedelta(days=days_ago)
        move.write({"state": "done", "date": date})
        return move

    def test_01_calc_flow_index_group_id(self):
        """The planned flow index group follows the buffer's order frequency."""
        self.buffer.cron_actions()
        self.assertEqual(self.buffer.order_frequency_group, 5)
        self.assertEqual(self.buffer.flow_index_group_id, self.flow_index_group_1)
        # Growing the order cycle grows the green zone -> order frequency -> group.
        self.buffer.order_cycle = 20
        self.buffer.cron_actions()
        self.assertEqual(self.buffer.order_frequency_group, 20)
        self.assertEqual(self.buffer.flow_index_group_id, self.flow_index_group_2)

    def test_02_flow_index_is_reactive(self):
        """flow_index_group_id is recomputed by the ORM on green zone / ADU change,
        without going through cron_actions."""
        self.buffer.cron_actions()
        self.assertEqual(self.buffer.flow_index_group_id, self.flow_index_group_1)
        # A direct write of the inputs re-triggers the stored computes.
        self.buffer.green_zone_qty = 80.0
        self.assertEqual(self.buffer.order_frequency_group, 20)
        self.assertEqual(self.buffer.flow_index_group_id, self.flow_index_group_2)

    def test_03_actual_flow_index(self):
        """The actual flow index reflects real completed replenishments."""
        self._create_done_receipt(days_ago=30)
        self._create_done_receipt(days_ago=120)
        self.buffer.cron_actions()
        self.assertEqual(self.buffer.actual_order_count, 2)
        # 365-day default horizon / 2 receipts -> ~183 day actual cycle.
        self.assertEqual(self.buffer.actual_order_frequency_group, 183)
        self.assertEqual(
            self.buffer.actual_flow_index_group_id, self.flow_index_group_3
        )

    def test_04_actual_flow_index_no_history(self):
        """No completed replenishments -> no actual flow index group."""
        self.buffer.cron_actions()
        self.assertEqual(self.buffer.actual_order_count, 0)
        self.assertFalse(self.buffer.actual_flow_index_group_id)

    def test_05_match_open_ended_and_gaps(self):
        """_match handles open-ended bounds (0 = unbounded) and unmatched gaps."""
        Group = self.env["ddmrp.flow.index.group"]
        Group.search([]).unlink()
        fast = Group.create(
            {"name": "Fast", "sequence": 1, "lower_range": 0, "upper_range": 5}
        )
        slow = Group.create(
            {"name": "Slow", "sequence": 2, "lower_range": 31, "upper_range": 0}
        )
        groups = Group.search([], order="sequence, id")
        self.assertEqual(groups._match(3), fast, "upper-only bound")
        self.assertEqual(groups._match(50), slow, "lower-only bound")
        self.assertFalse(groups._match(20), "value in the gap -> no group")
