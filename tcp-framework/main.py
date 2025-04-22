from pathlib import Path
from tcp_framework import (
    evaluate,
    Dataset,
)
from tcp_framework.approaches import (
    Approach,
    RandomOrder,
    FoldFailsOrder,
    TestLocOrder,
    RandomMixedOrder,
    BordaMixedOrder,
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
    RandomMixedOrder([FoldFailsOrder(), TestLocOrder()]),
    BordaMixedOrder([FoldFailsOrder(), TestLocOrder()]),
]

if __name__ == "__main__":
    rc_map = Dataset.preload_rc_map(Path("./datasets/tr_all_built_commits.csv"))

    datasets = [
        Dataset(runs_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), rc_map=rc_map)
        for repo in REPOS
    ]

    # for dataset in datasets:
    #     dataset.describe()

    for dataset in datasets:
        evaluate(APPROACHES, dataset, debug=1)
