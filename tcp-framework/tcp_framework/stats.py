from typing import Optional
import matplotlib.pyplot as plt

def metric_boxplot(file_path: str, values: list[list[float]], *, title: Optional[str] = None, labels: Optional[list[str]] = None) -> None:
    if labels is None:
        labels = [f"A{i+1}" for i in range(len(values))]
    assert len(values) == len(labels)

    plt.clf()
    plt.rcParams.update({"font.size": 12})
    if title is not None:
        plt.title(title)
    plt.xlabel("Approach")
    plt.ylabel("Value")
    plt.ylim(bottom=0.0, top=1.0)
    plt.boxplot(values, tick_labels=labels)
    plt.savefig(file_path)
