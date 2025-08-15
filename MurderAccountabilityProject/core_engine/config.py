# loads YAML once
from pathlib import Path
import yaml

_CFG = None

def get_cfg():
    global _CFG
    if _CFG is None:
        _CFG = yaml.safe_load(Path("policies.yaml").read_text(encoding="utf-8"))
    return _CFG
