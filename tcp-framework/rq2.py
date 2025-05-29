# (RQ2) Can approach combinators beat their sub-approaches in terms of effectiveness?

from pathlib import Path

from tcp_framework import Dataset, dump_results, evaluate
from tcp_framework.approaches import (
    BordaMixedOrder,
    CodeDistBreakedOrder,
    CodeDistOrder,
    ExeTimeOrder,
    FailDensityOrder,
    FoldFailsOrder,
    GenericBreakedOrder,
    InterpolatedOrder,
    RandomMixedOrder,
    RecentnessOrder,
    SchulzeMixedOrder,
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

    # (RQ2.1) Can mixers beat their sub-approaches in terms of effectiveness?
    print("=== rq21 ===")
    approaches = [
        FoldFailsOrder(seed=None),
        RecentnessOrder(latest_only=True),
        ExeTimeOrder(),
        BordaMixedOrder(
            [FoldFailsOrder(seed=None), RecentnessOrder(latest_only=True), ExeTimeOrder()],
            [1, 1, 0.5],
        ),
        RandomMixedOrder(
            [FoldFailsOrder(seed=None), RecentnessOrder(latest_only=True), ExeTimeOrder()],
            [1, 1, 0.5],
        ),
        SchulzeMixedOrder(
            [FoldFailsOrder(seed=None), RecentnessOrder(latest_only=True), ExeTimeOrder()],
            [1, 1, 0.5],
        ),
    ]
    for dataset in datasets:
        results = evaluate(
            approaches,
            dataset,
            ["rAPFDc"],
            debug=1,
        )
        dump_results(Path("./out/rq21.json"), dataset.name, [r.r_apfd_c_list for r in results])

    # (RQ2.2) Can interpolators beat their sub-approaches in terms of effectiveness?
    print("=== rq22 ===")
    approaches = [
        ExeTimeOrder(),
        RecentnessOrder(),
        FailDensityOrder(),
        InterpolatedOrder(BordaMixedOrder([ExeTimeOrder(), RecentnessOrder()]), 5, FailDensityOrder(), mode="failed"),
    ]
    for dataset in datasets:
        results = evaluate(
            approaches,
            dataset,
            ["rAPFDc"],
            debug=1,
        )
        dump_results(Path("./out/rq22.json"), dataset.name, [r.r_apfd_c_list for r in results])

    # (RQ2.3) Can tiebreakers beat their base approach in terms of effectiveness?
    print("=== rq23 ===")
    approaches = [
        FoldFailsOrder("total", seed=None),
        ExeTimeOrder(),
        CodeDistOrder(),
        GenericBreakedOrder(target=FoldFailsOrder("total", seed=None), breaker=ExeTimeOrder()),
        CodeDistBreakedOrder(target=FoldFailsOrder("total", seed=None)),
    ]
    for dataset in datasets:
        results = evaluate(
            approaches,
            dataset,
            ["rAPFDc"],
            debug=1,
        )
        dump_results(Path("./out/rq23.json"), dataset.name, [r.r_apfd_c_list for r in results])
