- Go to *Inventory \> Configuration \> DDMRP \> Flow Index Group* to define
  the groups (a name and an order-frequency range each). An unset bound is
  treated as open-ended.

Buffers are assigned to a group automatically -- the **planned** and **actual**
Flow Index Group are computed from the buffer's order frequency against those
ranges. The planned value updates whenever the buffer's green zone or ADU
change; the actual value is refreshed together with the buffer (the scheduled
*Buffer refresh* action, or the **Refresh Buffer** button). Changes to a group's
range therefore take effect on the next buffer refresh.
