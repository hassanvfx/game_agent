from pathlib import Path

paths = [
    Path("tools/game_matcher_fuzzy"),
    Path("tmp/run_game_matcher_fuzzy_examples.py"),
]

for path in paths:
    print(f"{path}: {'exists' if path.exists() else 'missing'}")