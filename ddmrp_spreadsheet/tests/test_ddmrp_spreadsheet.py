# Copyright 2025 Ledo Enterprises LLC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Tests for ddmrp_spreadsheet glue module.

Verifies that:
  - The demo spreadsheet is created with the expected pivot definitions.
  - The menu action exists and points to the correct model.
"""

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDdmrpSpreadsheet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.demo_ss = cls.env.ref(
            "ddmrp_spreadsheet.demo_buffer_dashboard", raise_if_not_found=False
        )

    def _skip_no_demo(self):
        if not self.demo_ss:
            self.skipTest("Demo data not loaded")

    def test_demo_spreadsheet_exists(self):
        self._skip_no_demo()
        self.assertEqual(self.demo_ss.name, "DDMRP Buffer Dashboard")

    def test_demo_spreadsheet_has_pivots(self):
        self._skip_no_demo()
        raw = self.demo_ss.spreadsheet_raw or {}
        pivots = raw.get("pivots", {})
        self.assertEqual(len(pivots), 4)
        models = {p.get("model") for p in pivots.values()}
        self.assertIn("stock.buffer", models)
        self.assertIn("ddmrp.history", models)

    def test_demo_spreadsheet_has_sheets(self):
        self._skip_no_demo()
        raw = self.demo_ss.spreadsheet_raw or {}
        sheets = raw.get("sheets", [])
        self.assertEqual(len(sheets), 4)
        names = {s["name"] for s in sheets}
        self.assertEqual(
            names, {"Buffer Status", "Zone Sizing", "Priority Review", "NFP History"}
        )

    def test_demo_refresh_schedule_exists(self):
        schedule = self.env.ref(
            "ddmrp_spreadsheet.demo_refresh_daily", raise_if_not_found=False
        )
        if not schedule:
            self.skipTest("Demo data not loaded")
        self._skip_no_demo()
        self.assertEqual(schedule.spreadsheet_id, self.demo_ss)

    def test_demo_subscription_exists(self):
        sub = self.env.ref(
            "ddmrp_spreadsheet.demo_sub_weekly", raise_if_not_found=False
        )
        if not sub:
            self.skipTest("Demo data not loaded")
        self._skip_no_demo()
        self.assertEqual(sub.spreadsheet_id, self.demo_ss)

    def test_menu_action_exists(self):
        action = self.env.ref(
            "ddmrp_spreadsheet.action_ddmrp_spreadsheets",
            raise_if_not_found=False,
        )
        self.assertTrue(action)
        self.assertEqual(action.res_model, "spreadsheet.spreadsheet")
