# (RQ3) What is the performance of the proposed approaches?

from pathlib import Path

from tcp_framework import Dataset, dump_results, evaluate
from tcp_framework.approaches import (
    Approach,
    BaseOrder,
    BordaMixedOrder,
    ExeTimeOrder,
    F2009Order,
    FailDensityOrder,
    FoldFailsOrder,
    GenericBreakedOrder,
    InterpolatedOrder,
    NameDispersityOrder,
    RandomOrder,
    RecentnessOrder,
    RocketOrder,
)

if __name__ == "__main__":
    cycle_map = Dataset.preload_cycle_map(Path("./datasets/travistorrent_8_2_2017.csv"), debug=True)
    datasets = [
        Dataset(cycles_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), cycle_map=cycle_map)
        for repo in [
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
    ]

    # print("=== baselines ===")
    # approaches: list[Approach] = [
    #     BaseOrder(),
    #     NameDispersityOrder(),
    #     RandomOrder(),
    #     F2009Order(),
    #     FoldFailsOrder(),
    #     FailDensityOrder(),
    #     RocketOrder(100),
    #     RocketOrder(1000),
    # ]
    # for dataset in datasets:
    #     results = evaluate(approaches, dataset, ["rAPFDc"], debug=1)
    #     dump_results(Path("./out/rq3-base.json"), dataset.name, [r.r_apfd_c_list for r in results])

    print("=== final ===")
    approaches = [
        RandomOrder(),
        FoldFailsOrder(),
        RocketOrder(100),
        BordaMixedOrder(
            [FoldFailsOrder(seed=None), RecentnessOrder(latest_only=True), ExeTimeOrder()],
            [1, 1, 0.5],
        ),
        InterpolatedOrder(BordaMixedOrder([ExeTimeOrder(), RecentnessOrder()]), 5, FailDensityOrder(), mode="failed"),
        GenericBreakedOrder(target=FoldFailsOrder("total", seed=None), breaker=ExeTimeOrder()),
    ]
    for dataset in datasets:
        results = evaluate(approaches, dataset, ["rAPFDc", "NTR", "ATR"], debug=1)
        dump_results(Path("./out/rq3-rapfdc.json"), dataset.name, [r.r_apfd_c_list for r in results])
        dump_results(Path("./out/rq3-ntr.json"), dataset.name, [[r.ntr_val] for r in results])
        dump_results(Path("./out/rq3-atr.json"), dataset.name, [[r.atr_val] for r in results])
