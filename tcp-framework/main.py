from pathlib import Path

from tcp_framework import Dataset, evaluate, metric_boxplot
from tcp_framework.approaches import (
    Approach,
    FailDensityOrder,
    FoldFailsOrder,
    RandomOrder,
)

REPOS = [
    "LittleProxy",
    "wicket-bootstrap",
    "titan",
    "dynjs",
    "jade4j",
    "jsprit",
    "optiq",
    "HikariCP",
    "DSpace",
    "cloudify",
    "okhttp",
    "graylog2-server",
]

APPROACHES: list[Approach] = [
    RandomOrder(),
    FoldFailsOrder(),
    FailDensityOrder(),
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
        calcs = evaluate(APPROACHES, dataset, ["rAPFDc"], debug=1)
        metric_boxplot(
            f"./out/rAPFDc-{dataset}.pdf",
            [c.r_apfd_c_list for c in calcs],
            title=f"rAPFDc - {dataset}",
            labels=["Random", "DFE", "Density"],
        )
