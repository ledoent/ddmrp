Bridges DDMRP with the OCA spreadsheet module to provide pre-built
dashboard templates for buffer monitoring.

Installs a demo spreadsheet with four pivot-connected sheets:

- **Buffer Status** — net flow position, qualified demand, and incoming
  supply grouped by warehouse and planning priority level.
- **Zone Sizing** — average red/yellow/green zone boundaries grouped by
  buffer profile, for reviewing sizing parameters.
- **Priority Matrix** — cross-tab of planning priority vs execution
  priority with average NFP% and on-hand%.
- **NFP History** — monthly trend of net flow position, zone boundaries,
  and ADU from ``ddmrp.history`` records.

A daily refresh schedule and weekly digest subscription are included as
demo data so the dashboard stays current out of the box.
