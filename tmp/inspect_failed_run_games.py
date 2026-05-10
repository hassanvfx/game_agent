#!/usr/bin/env python3
from pathlib import Path

RUN_DIR = Path("/Volumes/HDD2026/output/run_v4_brainrot_momsday_vatsal107_model55_c1_20260509T084144Z")
GAME_IDS = [
    "gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0",
    "gamezone-3fefc41a-1c39-4dcb-808f-183207e990e7",
    "gamezone-9dfd3280-7905-484c-a7cd-714850d499ee",
    "gamezone-e5885430-8061-42d3-a37c-7a341532f506",
    "gamezone-d81d4f32-e381-44a3-9e8f-d4ac09ddf35b",
]

for game_id in GAME_IDS:
    print(f"=== {game_id} ===")
    for section in ["input", "games", "output"]:
        path = RUN_DIR / section / game_id
        print(f"{section}: exists={path.exists()} is_dir={path.is_dir()}")
        if path.exists() and path.is_dir():
            children = sorted(path.iterdir())
            for child in children[:20]:
                kind = "dir" if child.is_dir() else "file"
                print(f"  {kind}: {child.name}")
            if len(children) > 20:
                print(f"  ... {len(children) - 20} more")

            if section == "games":
                op_dir = path / "operator_pipeline"
                print(f"  operator_pipeline_exists={op_dir.exists()} is_dir={op_dir.is_dir()}")
                if op_dir.exists() and op_dir.is_dir():
                    op_children = sorted(op_dir.rglob("*"))
                    for child in op_children[:40]:
                        rel = child.relative_to(path)
                        kind = "dir" if child.is_dir() else "file"
                        print(f"    {kind}: {rel}")
                    if len(op_children) > 40:
                        print(f"    ... {len(op_children) - 40} more")
    print()
