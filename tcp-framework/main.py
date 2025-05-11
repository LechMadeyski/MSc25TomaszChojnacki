from pathlib import Path

from tcp_framework import Dataset, evaluate
from tcp_framework.approaches import (
    Approach,
    CodeDistBreakedOrder,
    FailCodeDistOrder,
    FoldFailsOrder,
)
from tcp_framework.approaches.representation import StVectorizer

REPOS = [
    "LittleProxy",
    "HikariCP",
    "jade4j",
    "wicket-bootstrap",
    "titan",
    "dynjs",
    "jsprit",
    "DSpace",
    "optiq",
    "cloudify",
    "okhttp",
    "graylog2-server",
]

vectorizer = StVectorizer()

APPROACHES: list[Approach] = [
    FoldFailsOrder(),
    FailCodeDistOrder(vectorizer),
    CodeDistBreakedOrder(FoldFailsOrder("total", seed = None), vectorizer),
    CodeDistBreakedOrder(FoldFailsOrder("total"), vectorizer),
]

if __name__ == "__main__":
    cycle_map = Dataset.preload_cycle_map(Path("./datasets/travistorrent_8_2_2017.csv"), debug=True)

    datasets = [
        Dataset(cycles_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), cycle_map=cycle_map)
        for repo in REPOS
    ]

    # for dataset in datasets:
    #     dataset.describe()

    for dataset in datasets:
        evaluate(APPROACHES, dataset, ["rAPFDc"], debug=1)
