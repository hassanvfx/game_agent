# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
| --- | --- | --- | --- | --- | --- |
| Background music volume cap | `bgm.volume = 0.22` appears in audio init/resume paths in index.html. | Observation pass recorded bgm volume=0.2 after interaction, exceeding the 20% cap. | confirmed | fix | Hard audio safety rule requires looped audio at 20% or lower. |