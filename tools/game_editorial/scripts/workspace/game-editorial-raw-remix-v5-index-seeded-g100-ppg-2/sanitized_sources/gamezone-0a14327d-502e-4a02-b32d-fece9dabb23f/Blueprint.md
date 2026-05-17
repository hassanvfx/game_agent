# Blueprint

## High-level code structure
The game is a single-file HTML application with inline CSS and JavaScript rendered on a full-screen canvas, with HUD and modal UI layered on top using DOM elements. The structure breaks down into these major parts:

- **Presentation layer**
  - Full-screen `<canvas>` for all in-world rendering.
  - DOM HUD for money, level/unlock status, build buttons, and upgrade modal.
  - Inline CSS establishes a glossy sci-fi medical interface with mobile-safe layout.
- **Asset/config layer**
  - Embedded audio tags for BGM and SFX.
  - Embedded JSON config script defining treatment time, spawn rate, and unlock thresholds.
- **Runtime/gameplay layer**
  - Global state container `world` tracks currency, rooms, patients, particles, camera position, selection, and unlock flags.
  - Entity classes:
    - `Room`
    - `Patient`
    - `Particle`
  - Core systems:
    - spawning
    - room building
    - room upgrades
    - patient assignment
    - mental-state escalation
    - attack/failure events
    - particles/audio/gif feedback
- **Loop/input layer**
  - `requestAnimationFrame(loop)` drives update + draw.
  - Pointer drag scrolls vertically through the tower.
  - Pointer tap on rooms opens an upgrade modal.
  - Buttons build clinics and buy upgrades.

## Game loop / state model
The main runtime uses a simple continuous loop with two primary states:

- **`PLAYING`**
  - Updates spawning
  - Updates rooms/treatment timers
  - Updates patient state machines
  - Updates camera smoothing
  - Updates particles
  - Draws world every frame
- **`MODAL`**
  - Gameplay update pauses
  - Draw continues
  - Upgrade modal remains active
  - BGM pauses while the modal is open

### Core world state
The world tracks:
- **money** as the main resource
- **rooms** as the progression backbone and effective “level”
- **patients** as active service targets and threats
- **particles** as feedback only
- **cameraY / targetCameraY** for vertical tower navigation
- **selectedRoom** for upgrades
- **mentalUnlocked / paddedUnlocked** for phase progression

### Entity state models
**Room**
- `IDLE`
- `TREATING`

**Patient**
- `ENTERING`
- `WAITING`
- `WALKING_TO`
- `TREATING`
- `LEAVING`
- `ATTACKING`

Mental patients also track:
- `sanity`
- `mentalState`: `GREEN`, `YELLOW`, `RED`

## Player goals
The player’s short- and long-term goals appear to be:

1. **Earn Care Cash** by processing patients efficiently.
2. **Expand the clinic tower** by opening more treatment rooms.
3. **Upgrade room speed and payout** to improve throughput and income.
4. **Reach unlock milestones** for mental-care systems and calm suites.
5. **Stabilize dangerous patients** by building padded/calm rooms after they unlock.
6. **Prevent chaos and loss events** caused by untreated mental patients reaching red state and attacking others.

This creates a growth loop with a light crisis-management layer rather than a fail-state-heavy sim.

## Interaction pattern
The game is primarily a **tap-and-manage idle/active hybrid**:

- Tap **Open Clinic** to buy standard rooms.
- Later tap **Open Calm Suite** to buy specialized padded rooms.
- Tap a placed room to open an upgrade modal.
- In the modal, buy:
  - **Speed upgrades** to reduce treatment duration
  - **Value upgrades** to increase payout
- Drag vertically to inspect the tower as it grows.

The player does not directly move characters. Instead, they influence outcomes indirectly through construction and upgrades while autonomous agents handle service flow.

## Core systems

### 1. Clinic expansion system
- Starts with a reception/check-in room.
- New general clinics are added upward in alternating left/right positions.
- Room count effectively acts as progression level.
- Costs scale upward exponentially.

### 2. Automated patient flow system
- Patients spawn over time.
- They enter through reception, then get assigned to suitable rooms.
- If a valid room is idle, they walk there and begin treatment.
- On completion, they leave and generate money.

### 3. Upgrade economy
Each non-reception room has:
- **Speed level**
- **Value level**

Speed reduces treatment time multiplicatively.
Value increases payout multiplicatively.
Upgrade costs scale upward, reinforcing a compounding economy loop.

### 4. Mental-patient escalation system
After the unlock threshold:
- Some patients spawn as mental-health cases.
- Their sanity decays while untreated.
- They transition:
  - `GREEN` = stable
  - `YELLOW` = unstable, begins preferring padded room treatment
  - `RED` = fully escalated, becomes an attacker

This adds urgency and triage pressure.

### 5. Specialized room routing
Once padded rooms unlock:
- Mental patients in unstable states can reroute away from general rooms to padded rooms if available.
- Padded rooms fully calm them and restore sanity before payout.
- This functions like a specialized service lane.

### 6. Incident/combat-lite resolution
If a mental patient reaches red:
- They switch into `ATTACKING`
- They hunt another patient
- On contact, a hit effect plays
- The victim is removed
- The attacker is also removed/sedated

This is a soft-penalty system representing service breakdown rather than a combat game.

### 7. Feedback systems
The game uses layered reinforcement:
- particle text for rewards/upgrades/incidents
- SFX for clicks, money, calm, fail, alert
- vibration feedback
- GIF badges for calm success and danger spikes
- polished HUD and modal pauses

## Inferred genre / gameplay shape
Strongest inferred shape:

- **Hospital/clinic management arcade sim**
- **Light tycoon / resource-management game**
- **Single-screen vertical tower builder**
- **Casual mobile management game with autonomous agents**

It is not a deep simulation with staffing, scheduling, or multiple currencies. It is closer to a streamlined, approachable management-clicker where the player builds and upgrades service rooms while handling an emergent mental-care hazard system.

## Gameplay heuristic summary
The intended play heuristic appears to be:

- Build enough general clinics to scale revenue quickly.
- Upgrade speed early to improve throughput.
- Upgrade value as room count increases for stronger payout bursts.
- Rush toward unlock milestones.
- Once mental patients appear, introduce calm suites to absorb unstable cases.
- Maintain enough room capacity that patients do not idle long enough to become red-state threats.

In abstract terms, the game is about **growing a care tower while balancing efficiency and emotional stability**, framed through a bright, accessible medical-management fantasy.