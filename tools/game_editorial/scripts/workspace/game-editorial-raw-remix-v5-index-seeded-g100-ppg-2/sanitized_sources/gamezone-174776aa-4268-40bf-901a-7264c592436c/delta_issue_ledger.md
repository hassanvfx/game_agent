# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
| --- | --- | --- | --- | --- | --- |
| Choice feedback audio preload | Original success audio URL returned 404, and the first replacement also returned 404. Current markup uses approved `menu_open_01.mp3`, which is reachable. | Bounded response capture no longer shows a failing choice-audio URL after the final swap. | confirmed | fix | Minimal approved remote replacement removed a directly observed broken resource. |
| Looping background music preload | Original music loop URLs returned 404. Current markup uses approved `action_loop_01.mp3` and preserves the 20% volume cap. | Bounded response capture no longer shows a failing BGM URL after the final swap. | confirmed | fix | Minimal approved remote replacement removed a directly observed broken loop while keeping audio safety intact. |
| Core start flow and notebook menu | Embedded handlers wire start, first choice, and notebook menu flows. | Start flow, first choice, and notebook menu all worked in bounded mobile pass. | uncertain | leave_as_is | Browser evidence did not show a gameplay defect. |
