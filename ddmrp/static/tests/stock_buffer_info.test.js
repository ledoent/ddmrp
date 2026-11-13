/**
 * Copyright 2026 ForgeFlow S.L.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 */
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";
import {describe, expect, test} from "@odoo/hoot";

describe.current.tags("desktop");

const CHART = JSON.stringify({
    div: '<div class="o_test_buffer_div">chart</div>',
    script: "window.ddmrpBufferChartLoaded = true;",
});

class StockBuffer extends models.Model {
    _name = "stock.buffer";

    net_flow_position_percent = fields.Float();
    planning_priority_level = fields.Char();
    ddmrp_chart = fields.Text();

    _records = [
        {
            id: 1,
            net_flow_position_percent: 42.0,
            planning_priority_level: "1_red",
            ddmrp_chart: CHART,
        },
    ];
}

defineMailModels();
defineModels([StockBuffer]);

const ARCH = `
    <list>
        <field name="planning_priority_level" column_invisible="1"/>
        <field name="net_flow_position_percent" widget="stock_buffer_info"
               options='{"color_from": "planning_priority_level", "field": "ddmrp_chart"}'/>
    </list>`;

test("stock_buffer_info colours the circle from the priority level", async () => {
    await mountView({type: "list", resModel: "stock.buffer", arch: ARCH});
    // The widget only draws its circle in a readonly cell, which is how it is
    // used (list views). The class is derived from planning_priority_level
    // ("1_red"), so a bare (un-prefixed) template expression yields none.
    expect("span.circle").toHaveCount(1);
    expect("span.circle").toHaveClass("circle_red");
});
