# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import functools

from odoo import models

from odoo.addons.queue_job.job import identity_exact


class Buffer(models.Model):
    _inherit = "stock.buffer"

    def cron_actions_job_options(self, only_nfp=False):
        return {
            "identity_key": identity_exact,
            "priority": 15,
            "description": f"DDMRP Buffer calculation ({self.display_name})",
        }

    def _calc_adu_job_options(self):
        return {
            "identity_key": identity_exact,
            "priority": 15,
            "description": f"DDMRP Buffer ADU calculation ({self.display_name})",
        }

    def _register_hook(self):
        for method_name, context_key in (
            ("cron_actions", "auto_delay_ddmrp_cron_actions"),
            ("_calc_adu", "auto_delay_ddmrp_calc_adu"),
        ):
            patched = self._patch_job_auto_delay(method_name, context_key=context_key)
            setattr(
                type(self),
                method_name,
                functools.update_wrapper(patched, getattr(type(self), method_name)),
            )
        return super()._register_hook()

    def cron_ddmrp(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_cron_actions=True)
        ).cron_ddmrp(automatic=automatic, domain=domain)

    def cron_ddmrp_adu(self, automatic=False, domain=None):
        return super(
            Buffer, self.with_context(auto_delay_ddmrp_calc_adu=True)
        ).cron_ddmrp_adu(automatic=automatic, domain=domain)
