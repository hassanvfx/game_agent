#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


MANIFEST_PATH = Path(__file__).resolve().parent / "curated_limit2_prompt_only_manifest.json"

MOBILE_SUFFIX = (
    " with mobile-first controls, touch-friendly interactions, responsive readability, optimized on "
    "game start for portrait UI format, and the best-adapted mobile UX version targeting portrait "
    "aspect ratios in the 4:7 to 9:16 range."
)

CORRECTIONS: dict[str, tuple[str, str]] = {
    "Game of Thrones dark fantasy strategy RPG": (
        "dynasty strategy drama",
        "Dynasty strategy drama. A satirical game inspired by Game of Thrones with warring houses, political betrayal, dragons, icy apocalypse tension, brutal succession conflict, medieval grandeur, and high-stakes power games"
        + MOBILE_SUFFIX,
    ),
    "cozy kingdom builder": (
        "dynasty strategy drama",
        "Dynasty strategy drama. A satirical game inspired by Game of Thrones with warring houses, political betrayal, dragons, icy apocalypse tension, brutal succession conflict, medieval grandeur, and high-stakes power games"
        + MOBILE_SUFFIX,
    ),
    "Breaking Bad crime escalation strategy": (
        "crime escalation strategy",
        "Crime escalation strategy. A satirical game inspired by Breaking Bad with moral collapse, chemistry-driven schemes, cartel danger, suburban dread, transformation under pressure, dark irony, and consequence-heavy choices"
        + MOBILE_SUFFIX,
    ),
    "text thread detective": (
        "crime escalation strategy",
        "Crime escalation strategy. A satirical game inspired by Breaking Bad with moral collapse, chemistry-driven schemes, cartel danger, suburban dread, transformation under pressure, dark irony, and consequence-heavy choices"
        + MOBILE_SUFFIX,
    ),
    "Twilight romance fantasy": (
        "forbidden romance fantasy",
        "Forbidden romance fantasy. A satirical game inspired by Twilight with immortal longing, moody forests, supernatural love triangles, forbidden attraction, melodrama, rain-soaked yearning, and teenage obsession"
        + MOBILE_SUFFIX,
    ),
    "closet outfit sorter": (
        "forbidden romance fantasy",
        "Forbidden romance fantasy. A satirical game inspired by Twilight with immortal longing, moody forests, supernatural love triangles, forbidden attraction, melodrama, rain-soaked yearning, and teenage obsession"
        + MOBILE_SUFFIX,
    ),
    "The Office workplace comedy sim": (
        "workplace cringe comedy",
        "Workplace cringe comedy. A satirical game inspired by The Office with awkward social mini-games, deadpan documentary humor, office politics, lovable incompetence, cringe timing, and mundane-chaos meme energy"
        + MOBILE_SUFFIX,
    ),
    "cafe order rush": (
        "workplace cringe comedy",
        "Workplace cringe comedy. A satirical game inspired by The Office with awkward social mini-games, deadpan documentary humor, office politics, lovable incompetence, cringe timing, and mundane-chaos meme energy"
        + MOBILE_SUFFIX,
    ),
    "Friday the 13th camp-slasher survival": (
        "camp slasher survival",
        "Camp slasher survival. A satirical game inspired by Friday the 13th with Jason Voorhees pursuit, isolated woods, improvised escape, brutal tension, teen-horror archetypes, and relentless masked fear"
        + MOBILE_SUFFIX,
    ),
    "haunted hotel hidden-object": (
        "camp slasher survival",
        "Camp slasher survival. A satirical game inspired by Friday the 13th with Jason Voorhees pursuit, isolated woods, improvised escape, brutal tension, teen-horror archetypes, and relentless masked fear"
        + MOBILE_SUFFIX,
    ),
    "Chucky killer-doll horror": (
        "killer doll horror",
        "Killer doll horror. A satirical game inspired by Chucky with toy-sized menace, domestic chaos, dark comedy violence, possession mythology, absurd horror energy, and sneaky close-quarters attacks"
        + MOBILE_SUFFIX,
    ),
    "ghost photo mystery": (
        "killer doll horror",
        "Killer doll horror. A satirical game inspired by Chucky with toy-sized menace, domestic chaos, dark comedy violence, possession mythology, absurd horror energy, and sneaky close-quarters attacks"
        + MOBILE_SUFFIX,
    ),
    "Exorcist possession-horror narrative": (
        "possession horror narrative",
        "Possession horror narrative. A satirical game inspired by The Exorcist with ritual dread, faith-versus-evil conflict, psychological torment, sacred imagery, claustrophobic escalation, and spiritual horror intensity"
        + MOBILE_SUFFIX,
    ),
    "witch potion merge": (
        "possession horror narrative",
        "Possession horror narrative. A satirical game inspired by The Exorcist with ritual dread, faith-versus-evil conflict, psychological torment, sacred imagery, claustrophobic escalation, and spiritual horror intensity"
        + MOBILE_SUFFIX,
    ),
    "Pink Floyd surreal psychedelic visual": (
        "surreal psychedelic visual",
        "Surreal psychedelic visual. A satirical game inspired by Pink Floyd with cosmic dreamscapes, album-art symbolism, floating architecture, existential imagery, color-soaked abstraction, and mind-bending musical atmosphere"
        + MOBILE_SUFFIX,
    ),
    "playlist mood matcher": (
        "surreal psychedelic visual",
        "Surreal psychedelic visual. A satirical game inspired by Pink Floyd with cosmic dreamscapes, album-art symbolism, floating architecture, existential imagery, color-soaked abstraction, and mind-bending musical atmosphere"
        + MOBILE_SUFFIX,
    ),
    "doomscroll reflex game": (
        "password panic meme",
        "Password panic meme. A first-world-problems meme game inspired by modern login misery, with verification-code purgatory, account-lockout frustration, security-theater absurdity, and bureaucratic digital suffering"
        + MOBILE_SUFFIX,
    ),
    "beauty shelf organizer": (
        "brunch problems meme",
        "Brunch problems meme. A satirical game inspired by avocado-toast millennial lifestyle culture, with aesthetic consumption, urban convenience struggles, tiny food drama, and self-aware luxury satire"
        + MOBILE_SUFFIX,
    ),
    "Futurama sci-fi comedy": (
        "retro-future comedy",
        "Retro-future comedy. A satirical game inspired by Futurama with retro-future satire, delivery-crew antics, goofy worldbuilding, deadpan robots, space misadventures, and smart-stupid humor balance"
        + MOBILE_SUFFIX,
    ),
    "delivery route dash": (
        "retro-future comedy",
        "Retro-future comedy. A satirical game inspired by Futurama with retro-future satire, delivery-crew antics, goofy worldbuilding, deadpan robots, space misadventures, and smart-stupid humor balance"
        + MOBILE_SUFFIX,
    ),
    "X-Men mutant-team strategy": (
        "mutant team strategy",
        "Mutant team strategy. A satirical game inspired by X-Men with outsider identity themes, ensemble powers, prejudice conflict, school-for-heroes dynamics, faction tension, and big ensemble comic drama"
        + MOBILE_SUFFIX,
    ),
    "idle hero collector": (
        "mutant team strategy",
        "Mutant team strategy. A satirical game inspired by X-Men with outsider identity themes, ensemble powers, prejudice conflict, school-for-heroes dynamics, faction tension, and big ensemble comic drama"
        + MOBILE_SUFFIX,
    ),
    "Akira cyberpunk rebellion": (
        "cyberpunk rebellion chase",
        "Cyberpunk rebellion chase. A satirical game inspired by Akira with psychic instability, neon urban decay, biker-gang speed, government conspiracy, explosive body horror, and apocalyptic youth unrest"
        + MOBILE_SUFFIX,
    ),
    "neon scooter dodger": (
        "cyberpunk rebellion chase",
        "Cyberpunk rebellion chase. A satirical game inspired by Akira with psychic instability, neon urban decay, biker-gang speed, government conspiracy, explosive body horror, and apocalyptic youth unrest"
        + MOBILE_SUFFIX,
    ),
}


def main() -> int:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    runs = payload.get("runs")
    if not isinstance(runs, list):
        raise SystemExit("manifest runs must be a list")

    replaced: list[dict[str, str]] = []
    for item in runs:
        if not isinstance(item, dict):
            continue
        old_prompt = item.get("prompt")
        if not isinstance(old_prompt, str):
            continue
        replacement = CORRECTIONS.get(old_prompt)
        if replacement is None:
            continue
        new_prompt, new_remix_prompt = replacement
        item["prompt"] = new_prompt
        item["remix_prompt"] = new_remix_prompt
        replaced.append({"from": old_prompt, "to": new_prompt})

    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "manifest_path": str(MANIFEST_PATH),
                "replacement_count": len(replaced),
                "replacements": replaced,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())