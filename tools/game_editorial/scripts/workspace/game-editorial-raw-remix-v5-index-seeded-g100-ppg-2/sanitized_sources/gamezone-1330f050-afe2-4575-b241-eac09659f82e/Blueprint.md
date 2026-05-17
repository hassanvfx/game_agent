# Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS and JavaScript.
- `canvas#game-layer` renders the strategic map, regions, troop movements, and tactical overlays.
- DOM UI layer handles menus, HUD, pause screen, game-over modal, and GIF feedback badges.
- Core JavaScript sections:
  - data definitions: `NODES_DEF`, `EDGES`, `CATALOG_MEDIA`, `CFG`
  - systems: `AudioEngine`
  - entities: `Node`, `Troop`
  - orchestration: `Game`
  - presentation/UI helpers: `UI`

## Game loop / state model
- Main states: `INIT`, `SELECT`, `PLAY`, `PAUSE`, `OVER`.
- `window.onload -> Game.init()` builds factions, nodes, neighbors, input bindings, and starts `requestAnimationFrame`.
- During `SELECT`, the player chooses one starting region/command hub.
- `startMatch()` assigns every node to a unique faction, marks all as capitals, and begins real-time simulation.
- During `PLAY`, each frame:
  - updates timers and speed scaling
  - regenerates troop counts on owned nodes
  - advances moving troop packets
  - resolves combat/capture on arrival
  - runs AI every 0.5 seconds
  - checks win/loss conditions
- `PAUSE` freezes simulation but preserves board state.
- `OVER` shows win/loss modal and end-state feedback.

## Player goals
- Select an opening command hub.
- Expand from the chosen faction across the network graph.
- Defend your own capital chain while conquering enemy capitals.
- Eliminate all opposing factions by taking over their territories until the entire map is under your control.

## Interaction pattern
- Pre-match: tap/click any region to choose a starting hub, then press the start button.
- In play: drag from a player-owned neighboring region onto an adjacent target to send half the source troop count.
- Optional tactical button:
  - `Signal Burst / Jammer` temporarily prevents AI raids into player-held territories.
- Meta controls:
  - speed cycling (`1x`, `2x`, `4x`, `½x`)
  - pause/resume
  - music on/off and track switch

## Core systems
- **Graph-based territory control:** regions are polygons with explicit adjacency from `EDGES`.
- **Population/troop generation:** owned nodes periodically grow troop counts up to a devastation-reduced cap.
- **Mobile troop packets:** dispatched forces travel as moving units between connected nodes.
- **Combat resolution:** arrivals reinforce allies or subtract from enemies; conquered nodes flip owner.
- **Capital annexation:** capturing an enemy capital instantly converts all of that faction's remaining nodes and active troops.
- **Devastation model:** attacks permanently increase a node's devastation, reducing capacity while also increasing production tempo.
- **AI pressure:** every enemy faction evaluates nearby opportunities and occasionally launches attacks or reinforcements.
- **Presentation feedback:** audio, HUD state, impact/victory GIF badges, and annex toast notifications reinforce important events.

## Inferred genre / gameplay shape
- Real-time minimalist strategy game on a territorial node graph.
- Closest shape: graph-conquest RTS / territory domination skirmish.
- Feels like a compact browser adaptation of games where players route units between connected regions and snowball by capturing capitals.
- Thematic wrapper shifts the map war fantasy into a cyber-radio “signal dominance” fiction, but the underlying play is conquest strategy.

## Gameplay heuristic
- Early game likely rewards choosing a well-connected central hub for expansion flexibility.
- Sending exactly half the troops encourages repeated short routing decisions instead of all-in dumping.
- Enemy capitals are disproportionately valuable because annexation creates sudden board swings.
- The jammer/peace burst is a defensive tempo tool for surviving multi-front pressure, not a full ceasefire.
- Speed controls imply the game is intended for active pacing management and board-reading rather than twitch execution.
