from pathlib import Path

paths = [
    "games/published/public/gamezone-a8546a14-d978-4cf8-9a51-9ff454a540b1/remix-d2bd7602d47f056c5d7358e08ecd50b4",
    "games/published/public/gamezone-5fbc49e4-d93b-46c7-97e5-7de892ba3ac0/remix-da21295f7b2d9c7ddc2e61d2d4658be4",
]

for raw in paths:
    path = Path(raw)
    print(
        {
            "path": raw,
            "exists": path.exists(),
            "is_dir": path.is_dir(),
            "index_exists": (path / "index.html").exists(),
        }
    )