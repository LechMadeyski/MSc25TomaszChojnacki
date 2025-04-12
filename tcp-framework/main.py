from pathlib import Path
from tcp_framework import (
    evaluate,
    Approach,
    Dataset,
    RandomOrder,
    FoldFailuresOrder,
    TestLocOrder,
    FaultCodeDistOrder,
    EuclidDist,
    MinAgg,
    StVectorizer,
)

approaches: list[Approach] = [
    RandomOrder(),
    FoldFailuresOrder("dfe"),
    TestLocOrder(),
    FaultCodeDistOrder(StVectorizer(), EuclidDist(), MinAgg()),
]

repos = [
    "adamfisk@LittleProxy",
    "brettwooldridge@HikariCP",
    "jOOQ@jOOQ",
    "neuland@jade4j",
    "CloudifySource@cloudify",
    "DSpace@DSpace",
    "dynjs@dynjs",
    "Graylog2@graylog2-server",
    "doanduyhai@Achilles",
]
# TODO: deeplearning4j, buck

rc_map = Dataset.preload_rc_map(Path("./datasets/tr_all_built_commits.csv"))

for repo in repos:
    evaluate(
        approaches,
        Dataset(
            runs_path=Path(f"./datasets/{repo}.csv"),
            repo_path=Path(f"./datasets/{repo.split('@')[1]}"),
            rc_map=rc_map,
        ),
        debug=1,
    )
