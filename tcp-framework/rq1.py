# (RQ1) What is the impact of the parameters of CodeDistOrder on its effectiveness?

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import cast

from tcp_framework import Dataset, dump_results, evaluate
from tcp_framework.approaches import Approach, CodeDistOrder
from tcp_framework.approaches.representation import GroupAgg, Normalization, StVectorizer, VectorDist


def run_subquestion[T](
    datasets: Sequence[Dataset], filename: str, options: Sequence[T], factory: Callable[[T], Approach]
) -> None:
    print(f"=== {filename} ===")
    approaches = [factory(option) for option in options]
    for dataset in datasets:
        results = evaluate(
            approaches,
            dataset,
            ["rAPFD"],
            debug=1,
        )
        dump_results(Path(f"./out/{filename}.json"), dataset.name, [r.r_apfd_list for r in results])


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
            "graylog2-server",
        ]
    ]

    # (RQ1.1) How does the choice of normalization type affect CodeDistOrder's effectiveness?
    run_subquestion(
        datasets,
        "rq11",
        cast("list[Normalization]", [None, "formatting", "identifiers"]),
        lambda normalization: CodeDistOrder(StVectorizer(normalization=normalization)),
    )

    # (RQ1.2) How does the choice of vector distance affect CodeDistOrder's effectiveness?
    run_subquestion(
        datasets, "rq12", [VectorDist.mann, VectorDist.euclid], lambda distance: CodeDistOrder(distance=distance)
    )

    # (RQ1.3) How does the choice of aggregation function affect CodeDistOrder's effectiveness?
    run_subquestion(
        datasets,
        "rq13",
        [GroupAgg.min, GroupAgg.avg, GroupAgg.max],
        lambda aggregation: CodeDistOrder(aggregation=aggregation),
    )
