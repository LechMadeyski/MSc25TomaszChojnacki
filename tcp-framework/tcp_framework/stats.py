import json
from collections.abc import Sequence
from pathlib import Path


def dump_results(file_path: Path, key: str, results: Sequence[Sequence[float]]) -> None:
    content: dict[str, Sequence[Sequence[float]]] = {}
    try:
        with Path.open(file_path, "r") as f:
            content = json.load(f)
    except Exception:
        pass

    content[key] = results

    with Path.open(file_path, "w") as f:
        json.dump(content, f, indent=2)
