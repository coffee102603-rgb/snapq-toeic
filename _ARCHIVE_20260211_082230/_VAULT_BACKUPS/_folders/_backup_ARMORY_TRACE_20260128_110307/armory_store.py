import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ARMORY_PATH = Path("app/data/armory/secret_armory.json")
MAX_LIMIT = 1200

def _safe_load_json(path: Path, default: Any):
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default

def _safe_save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_armory_items() -> List[Dict[str, Any]]:
    d = _safe_load_json(ARMORY_PATH, [])
    if isinstance(d, dict):
        items = d.get("items", [])
        return items if isinstance(items, list) else []
    return d if isinstance(d, list) else []

def save_armory_items(items: List[Dict[str, Any]]) -> None:
    _safe_save_json(ARMORY_PATH, items[:MAX_LIMIT])

def append_item(item: Dict[str, Any]) -> None:
    items = load_armory_items()
    items.append(item)
    save_armory_items(items)

def append_p7_vocab(word: str, meaning: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """✅ P7에서 저장되는 '진짜 VOCA' 표준 포맷."""
    word = (word or "").strip()
    meaning = (meaning or "").strip()
    if not word or not meaning:
        return

    payload: Dict[str, Any] = {
        "source": "P7",
        "mode": "p7_vocab",
        "word": word,
        "meaning": meaning,
    }
    if isinstance(extra, dict):
        payload.update(extra)

    append_item(payload)
