#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module():
    module_path = Path("tools/game_generator/scripts/demo_pipeline_launch.py")
    spec = importlib.util.spec_from_file_location("demo_pipeline_launch", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    mod = load_module()
    parser = mod.parse_args

    original_argv = sys.argv[:]
    try:
        sys.argv = [
            "demo_pipeline_launch.py",
            "mario world 2d game",
            "--poll-seconds",
            "7",
            "--remix-prompt",
            "mario world pastel remix",
            "--upload",
            "--obfuscate",
            "--no-open",
        ]
        args = parser()
        command = mod.build_pipeline_command(args)
    finally:
        sys.argv = original_argv

    print(json.dumps({"command": command}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())