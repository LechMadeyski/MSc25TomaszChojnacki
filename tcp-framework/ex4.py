from pathlib import Path

from tcp_framework import Dataset, evaluate, metric_boxplot
from tcp_framework.approaches import (
    Approach,
    BordaMixedOrder,
    CodeDistOrder,
    ExeTimeOrder,
    FailCodeDistOrder,
    FailDensityOrder,
    FoldFailsOrder,
    RandomMixedOrder,
    RandomOrder,
    RecentnessOrder,
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
]

vectorizer = StVectorizer("microsoft/unixcoder-base")

APPROACHES: list[Approach] = [
    RandomOrder(),
    FoldFailsOrder(),
    CodeDistOrder(vectorizer),
    FailCodeDistOrder(vectorizer),
    BordaMixedOrder(
        [FoldFailsOrder(), FoldFailsOrder("total"), FailDensityOrder(), ExeTimeOrder(), RecentnessOrder()],
        [0.9, 1.0, 0.5, 0.75, 0.5],
    ),
    RandomMixedOrder([FoldFailsOrder(), FoldFailsOrder("total"), ExeTimeOrder()], [0.5, 0.6, 0.35]),
]

if __name__ == "__main__":
    cycle_map = Dataset.preload_cycle_map(Path("./datasets/travistorrent_8_2_2017.csv"), debug=True)

    datasets = [
        Dataset(cycles_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), cycle_map=cycle_map)
        for repo in REPOS
    ]

    for dataset in datasets:
        calcs = evaluate(APPROACHES, dataset, ["ATR"], debug=1)
        metric_boxplot(
            f"./out/ex4-rAPFDc-{dataset.name}.pdf",
            [c.r_apfd_c_list for c in calcs],
            title=f"rAPFDc - {dataset.name}",
            labels=["Rnd", "DFE", "CRSim", "CRFails", "BordaMix", "RndMix"],
        )
