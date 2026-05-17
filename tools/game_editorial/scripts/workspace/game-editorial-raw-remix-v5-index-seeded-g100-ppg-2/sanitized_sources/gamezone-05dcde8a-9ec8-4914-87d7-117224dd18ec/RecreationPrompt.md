# Recreation Prompt

Create a polished, mobile-friendly 2D browser arcade game called **Melody Bus Run**. The game should feel like a colorful neon endless runner with strong musical personality. The player controls a cute anthropomorphic bus with a face that drives through a glowing night roadway while singing cheerful lyric snippets. The bus should stay near the left side of the screen, and the world should auto-scroll so hazards and collectibles approach from the right.

Use a **single-action control scheme**: tapping/clicking or pressing **Space**, **Arrow Up**, or **Arrow Down** should switch the bus between **exactly two lanes**. There should be no free movement, no steering, and no braking. The gameplay loop is simple and replayable: start the run, read which lane is safe, swap lanes at the right moment, collect glowing music notes for points, avoid sharp roadblock rocks, and survive as long as possible while speed gradually increases.

Build the run around **two object types**:
- **Collectible glowing notes** that award 1 point each and trigger satisfying celebratory feedback.
- **Roadblock hazards** that instantly end the run on contact.

The challenge should come from **lane-reading and timing under rising speed**, not from complex systems. Keep the structure endless and score-based rather than level-based. When the player crashes, show a strong fail state with a game-over panel, the final score, and a clear replay button for instant restart.

The presentation should be bright and arcade-like:
- fullscreen canvas playfield
- deep blue to neon sky gradients
- glowing atmosphere and arcade UI panels
- stylized road with dashed lane divider
- soft clouds, roadside trees, and parallax scenery
- a lively bus character with bounce animation and a mouth that opens while singing
- glowing note collectibles and jagged rock obstacles
- HUD score display and a mute button
- flashy start screen and game-over screen

Audio and character performance are essential signature features. Include:
- looping background music
- small synthesized melody notes that play continuously during the run
- speech-synthesis or announcer-style vocal lines so the bus “sings” short phrases
- speech-bubble lyric text appearing near the bus
- lane-switch, collect, crash, start, mute, and game-over sound feedback

Use celebratory particles and positive visual reinforcement when collecting notes, plus a more intense crash burst on failure. The tone should remain **playful, family-friendly, rhythmic, energetic, and instantly readable**, like a casual mobile arcade runner wrapped in a karaoke-neon road-show theme. The final result should feel like a simple but charming two-lane endless runner whose identity comes from its singing bus, glowing musical notes, and vibrant night-drive spectacle.