from pathlib import Path

from bayes_opt import BayesianOptimization

from tcp_framework import Dataset, evaluate
from tcp_framework.approaches import (
    ExeTimeOrder,
    FailDensityOrder,
    FoldFailsOrder,
    RandomMixedOrder,
    RecentnessOrder,
)

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
]

if __name__ == "__main__":
    cycle_map = Dataset.preload_cycle_map(Path("./datasets/travistorrent_8_2_2017.csv"), debug=True)

    datasets = [
        Dataset(cycles_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), cycle_map=cycle_map)
        for repo in REPOS
    ]

    def target(*, dfe: float, tot: float, den: float, exe: float, rct: float) -> float:
        approach = RandomMixedOrder(
            targets=[
                FoldFailsOrder(),
                FoldFailsOrder("total"),
                FailDensityOrder(),
                ExeTimeOrder(),
                RecentnessOrder(),
            ],
            weights=[dfe, tot, den, exe, rct],
        )
        return sum(evaluate([approach], dataset)[0].r_apfd_c_avg for dataset in datasets) / len(datasets)

    optimizer = BayesianOptimization(
        f=target,
        pbounds={k: (0.0, 1.0) for k in ["dfe", "tot", "den", "exe", "rct"]},
        random_state=0,
    )

    optimizer.maximize(
        init_points=10,
        n_iter=40,
    )

    print(optimizer.max)
