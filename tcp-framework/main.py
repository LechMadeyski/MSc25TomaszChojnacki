from pathlib import Path
from tcp_framework import (
    evaluate,
    Approach,
    Dataset,
    RandomOrder,
    FoldFailuresOrder,
    FaultCodeDistOrder,
)
from tcp_framework.approaches.representation import EuclidDist, MinAgg, StVectorizer

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

vectorizer = StVectorizer()

APPROACHES: list[Approach] = [
    RandomOrder(),
    FoldFailuresOrder("dfe"),
    FaultCodeDistOrder(vectorizer, EuclidDist(), MinAgg()),
]

if __name__ == "__main__":
    rc_map = Dataset.preload_rc_map(Path("./datasets/tr_all_built_commits.csv"))

    datasets = [
        Dataset(runs_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), rc_map=rc_map)
        for repo in REPOS
    ]

    print("=== DATASETS ===")
    for dataset in datasets:
        dataset.describe()

    print("\n=== APPROACHES ===")
    for dataset in datasets:
        evaluate(APPROACHES, dataset, debug=1)
