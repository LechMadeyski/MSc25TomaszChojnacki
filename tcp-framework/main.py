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
    StVectorizer
)

approaches: list[Approach] = [
    RandomOrder(),
    FoldFailuresOrder("dfe"),
    TestLocOrder(),
    FaultCodeDistOrder(StVectorizer(), EuclidDist(), MinAgg()),
]

repos = ["jOOQ@jOOQ", "adamfisk@LittleProxy", "brettwooldridge@HikariCP",
         "neuland@jade4j", "CloudifySource@cloudify", "DSpace@DSpace",
         "dynjs@dynjs", "Graylog2@graylog2-server", "doanduyhai@Achilles"]
# TODO: deeplearning4j, buck

for repo in repos:
    dataset = Dataset(
        runs_path=f"./datasets/{repo}.csv",
        repo_path=f"./datasets/{repo.split('@')[1]}",
        run_to_commit_path="./datasets/tr_all_built_commits.csv",
    )
    evaluate(approaches, dataset, debug=1)
    del dataset
