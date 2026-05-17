# Delta Issue Ledger

## Candidate Issue
1. **Observed area** - core scan flow
2. **Static evidence** - Roll handler debits cost, reveals weighted rarity, applies payout, and unlocks archive entry.
3. **Browser evidence** - Initial scan completed successfully with revealed card and updated balance in screenshots.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - No breakage observed during bounded mobile pass.

## Candidate Issue
1. **Observed area** - archive navigation
2. **Static evidence** - Navigation stack and renderAlmanac() populate archive entries from unlocked set.
3. **Browser evidence** - Archive opened and showed progress count after one reveal.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - Interaction worked in bounded mobile pass.

## Candidate Issue
1. **Observed area** - looping background music volume
2. **Static evidence** - bgm.volume had been set above the 20% maximum for looping audio; it is now set to 0.2 in audio.init().
3. **Browser evidence** - Runtime check after launch reported bgm.volume=0.2, satisfying the cap, and the rest of the bounded flow remained functional.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Looping audio must remain at or below the mandated 20% cap.
