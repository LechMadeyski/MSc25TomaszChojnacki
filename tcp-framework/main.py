from pathlib import Path
from tcp_framework import (
    evaluate,
    Approach,
    Dataset,
    RandomOrder,
    FoldFailsOrder,
    FailCodeDistOrder,
)
from tcp_framework.approaches.representation import StVectorizer

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
    FailCodeDistOrder(StVectorizer()),
]

if __name__ == "__main__":
    rc_map = Dataset.preload_rc_map(Path("./datasets/tr_all_built_commits.csv"))

    datasets = [
        Dataset(runs_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), rc_map=rc_map)
        for repo in REPOS
    ]

    for dataset in datasets:
        evaluate(APPROACHES, dataset, debug=1)
