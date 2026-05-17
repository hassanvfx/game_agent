# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
| --- | --- | --- | --- | --- | --- |
| runner pre-start flow | The loop began updating immediately on load(), allowing runner gravity and hazards to progress before player input. | Post-fix mobile pass showed the runner overlay staying idle with the start hint visible until the first tap. | confirmed | fix | A pre-start idle overlay should not allow the run to fail before the player begins. |
| audio loop levels | Looped tracks use 0.22 and 0.18 volume. | No audio breakage observed during bounded pass. | confirmed | leave_as_is | Continuous audio remains at or below the 20% cap for gameplay and near-cap menu loop; no increase was introduced. |