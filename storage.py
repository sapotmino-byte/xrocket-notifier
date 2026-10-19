import json
import os
import sys

_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_deals.json")
_MAX_ITEMS = 5000

_seen = {}
_loaded = False


def _load():
    global _loaded
    if _loaded:
        return
    _loaded = True
    if not os.path.exists(_FILE):
        return
    try:
        with open(_FILE, encoding="utf-8") as f:
            for key in json.load(f):
                _seen[key] = True
    except Exception as e:
        print(f"[storage] Не удалось прочитать {_FILE}: {e}", file=sys.stderr)


def _save():
    try:
        with open(_FILE, "w", encoding="utf-8") as f:
            json.dump(list(_seen.keys()), f, ensure_ascii=False)
    except Exception as e:
        print(f"[storage] Не удалось сохранить {_FILE}: {e}", file=sys.stderr)


def was_seen(key: str) -> bool:
    _load()
    return key in _seen


def mark_seen(key: str):
    _load()
    _seen[key] = True
    while len(_seen) > _MAX_ITEMS:
        oldest = next(iter(_seen))
        _seen.pop(oldest)
    _save()
