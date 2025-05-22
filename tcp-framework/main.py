from pathlib import Path

from tcp_framework import Dataset, evaluate
from tcp_framework.approaches import Approach, ExeTimeOrder, FailDensityOrder, FoldFailsOrder, GenericBreakedOrder

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

APPROACHES: list[Approach] = [
    FoldFailsOrder(),
    FailDensityOrder(),
    GenericBreakedOrder(target=FoldFailsOrder("total", seed=None), breaker=ExeTimeOrder()),
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
