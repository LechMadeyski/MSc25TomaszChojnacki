import json
from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt


def metric_boxplot(
    file_path: Path,
    values: Sequence[Sequence[float]],
    *,
    title: str | None = None,
    labels: Sequence[str] | None = None,
) -> None:
    if labels is None:
        labels = [f"A{i + 1}" for i in range(len(values))]
    assert len(values) == len(labels), "values and labels must have the same length"

    plt.clf()
    plt.rcParams.update({"font.size": 12})
    if title is not None:
        plt.title(title)
    plt.xlabel("Approach")
    plt.ylabel("Value")
    plt.ylim(bottom=0.0, top=1.0)
    plt.boxplot(values, tick_labels=labels)
    plt.savefig(file_path)


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
