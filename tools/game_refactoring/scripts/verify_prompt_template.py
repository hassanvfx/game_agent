from pathlib import Path
import sys
import importlib.util

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ropg", root / "scripts" / "run_operator_pipeline_game.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

run_dir = root / "runs" / "run_game_remixer_20260508T035141Z"
game_dir = run_dir / "games" / "gamezone-ea127465-3223-4053-af7b-2a61f74c312c"
run_state = module.load_json(run_dir / "run_state.json")
game_state = module.load_json(game_dir / "game_state.json")
nodes = module._read_manifest_nodes(run_dir)
operator = nodes[2]

text = module.build_operator_prompt_text(
    run_state=run_state,
    game_state=game_state,
    operator=operator,
    attempt_number=1,
    attempt_workspace=game_dir / "operator_pipeline" / operator.stage_slug / "attempt_01" / "workspace",
    previous_contract_status=None,
    previous_contract_detail=None,
)

print("#PROMPT# still present:", "#PROMPT#" in text)
print("--- PROMPT PREVIEW START ---")
for line in text.splitlines()[:120]:
    print(line)
print("--- PROMPT PREVIEW END ---")