from pathlib import Path

from tcp_framework import Dataset, evaluate
from tcp_framework.approaches import (
    BordaMixedOrder,
    ExeTimeOrder,
    FailDensityOrder,
    FoldFailsOrder,
    RandomOrder,
    RecentnessOrder,
    TestLocOrder,
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

    def target(*, rnd: float, dfe: float, tot: float, den: float, exe: float, loc: float, rct: float) -> float:
        approach = BordaMixedOrder(
            targets=[
                RandomOrder(),
                FoldFailsOrder(),
                FoldFailsOrder("total"),
                FailDensityOrder(),
                ExeTimeOrder(),
                TestLocOrder(),
                RecentnessOrder(),
            ],
            weights=[rnd, dfe, tot, den, exe, loc, rct],
        )
        return sum(evaluate([approach], dataset)[0].r_apfd_c_avg for dataset in datasets) / len(datasets)

    print(target(rnd=0.1, dfe=0.1, tot=0.1, den=0.1, exe=0.1, loc=0.1, rct=0.1))
