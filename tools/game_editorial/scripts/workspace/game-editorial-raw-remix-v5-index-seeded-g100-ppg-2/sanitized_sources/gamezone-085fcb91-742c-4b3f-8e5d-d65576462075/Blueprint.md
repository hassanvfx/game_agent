# Blueprint

## High-level code structure
The game is implemented as a single self-contained `index.html` document with:
- inline CSS for the neon arcade presentation, HUD, modal menus, mobile controls, and feedback overlays
- inline JavaScript for state, entities, input handling, audio/GIF feedback, rendering, and UI wiring
- a single canvas for core playfield rendering, plus DOM overlays for menus, HUD, action prompts, and touch controls

Main code layers inferred from the source:
1. **Configuration/constants**
   - recipe definitions
   - staff role definitions
   - economy and capacity constants
2. **Global game state**
   - money, ingredients, dishes, wages
   - room ownership and tables
   - staff counts
   - pending orders and cooked food queue
   - entity list and floating text effects
3. **Systems**
   - touch joystick/action button input
   - audio playback using approved remote audio URLs
   - success/warning GIF feedback overlays
4. **Entities**
   - `Player`
   - `Staff`
   - `Customer`
   - `Table`
5. **Core loop**
   - `init()`
   - `loop(timestamp)`
   - `update(dt)`
   - `draw()`
6. **Gameplay helpers/UI**
   - cooking modal
   - upgrade/recruitment menu
   - economy actions such as buying supplies, tables, and unlocking wings

## Game loop / state model
The game uses a real-time requestAnimationFrame loop.

### Top-level states
- `MENU`: start screen visible, game not running
- `PLAYING`: simulation active, input and spawning active
- `MODAL`: gameplay visually paused while cook/upgrade UI is open

### Simulation loop behavior
During `PLAYING`, each frame:
1. wage timer counts down and pays staff every 60 seconds
2. customer spawn timer advances and adds a new customer roughly every 8 seconds if queue pressure is low
3. entities update in y-sorted order
4. contextual interaction checks run if the player is not already busy
5. floating text effects advance
6. HUD values refresh
7. canvas redraw renders current room and entities

### Player-local state
The player can be:
- moving freely
- holding cooked food
- locked in a timed action
- locked in a training state

Timed actions include:
- cooking manually
- washing trays manually
- training a crew member

### World model
The world is split into three horizontal rooms/wings:
- west wing
- center kitchen/service wing
- east wing

The player walks between rooms by crossing screen edges. Only owned wings are operational; locked wings show a purchase prompt.

## Player goals
Primary goal:
- grow a snack-service arcade business by serving customers efficiently and earning money

Operational goals:
- take customer orders
- cook matching food combos
- deliver the correct food to the correct table
- collect money from completed tables
- restock ingredients and wash trays
- recruit automation staff
- train staff to improve performance
- buy more booths/tables
- unlock additional wings for more seating capacity

Failure pressure is soft rather than terminal:
- customers can leave angry if they wait too long
- payroll drains profits over time
- wrong food, low ingredients, or no trays slow progression

## Interaction pattern
The game is designed first for mobile touch play.

### Core controls
- **virtual joystick**: move the player
- **single action button**: context-sensitive interaction

### Context-sensitive actions
Depending on proximity, the same action button is used to:
- take an order at the counter
- open the cooking menu or pick up ready food at the grill
- wash trays at the sink
- trash held food
- serve a table
- collect cash from a table
- train nearby staff
- unlock a new wing

This creates a one-avatar, one-button, proximity-driven management loop.

## Core systems

### 1. Restaurant/arcade service loop
The heart of the game is a streamlined service sim loop:
1. customers spawn
2. customer orders are taken
3. orders enter a pending queue
4. food is cooked manually or automatically
5. food is delivered to seated customers
6. customers eat, leave cash on tables, and depart
7. player or waiter collects the cash

### 2. Resource management
The player manages:
- **money**: used for staff, tables, ingredients, and wing unlocks
- **ingredients/supplies**: consumed by cooking
- **clean trays/dishes**: consumed when producing food, replenished by washing

The dual-consumable structure creates a light multitasking economy loop.

### 3. Staff automation
Recruitable staff roles automate different parts of the loop:
- **cashier**: auto-takes queued orders
- **chef**: auto-cooks pending orders
- **waiter**: auto-collects money from tables
- **washer**: auto-refills trays when low

This shifts the game from fully manual play toward semi-automated management.

### 4. Staff training / upgrading
Crew members can be trained in-world by standing near them and paying money to begin a 10-second drill.
Training:
- levels up that specific staff unit
- increases work speed
- acts like an active upgrade mechanic layered onto automation

### 5. Expansion
The business expands through:
- buying extra tables in the current owned room
- unlocking side wings for a large cost

This increases seating throughput and long-term earning potential.

### 6. Patience and throughput pressure
Customers carry a wait timer while seated/waiting for food.
If service is too slow:
- the customer leaves angry
- the table is freed
- the order opportunity is lost

This creates time pressure without direct combat or failure screens.

### 7. Presentation feedback
The game uses:
- floating text for rewards/errors/status
- HUD pulses for low resources
- success/warning GIF popups
- arcade-styled sound feedback
- modal menus for cooking and upgrades

## Inferred genre / gameplay shape
Strongest inferred shape:
- **light restaurant management / cooking game with direct avatar control**

More specifically, it feels like:
- a mobile-friendly real-time service sim
- a casual arcade management game
- a hybrid of manual cooking-service play and automation/tycoon progression

The “arcade” theme is largely a presentation wrapper over a restaurant/snack-stand management loop. The player is not playing arcade minigames; they are running a neon snack venue with crew management and room expansion.

## Gameplay heuristic summary
A player likely experiences the game as:
- start with a small central snack area
- manually handle orders, cooking, serving, washing, and collecting
- stabilize the economy
- recruit staff to automate bottlenecks
- train staff for efficiency
- buy more booths and unlock more wings
- keep throughput high enough to outpace customer impatience and payroll drain

## Confidence notes
High confidence:
- manual service loop
- touch-based movement/action controls
- staff roles and automation
- room expansion structure
- resource and payroll systems

Moderate confidence:
- intended long-term pacing beyond the current three-room layout
- whether the “arcade” theme is meant as a restaurant-in-an-arcade venue or a stylized branding layer

Low confidence:
- presence of any planned endgame/win state, because no explicit victory condition exists in the code