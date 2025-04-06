from tcp_framework import (
    evaluate,
    TcpApproach,
    TcpDataset,
    CodeDistOrder,
    BaseOrder,
    RandomOrder,
    CodeXEmbed,
    EuclidDist,
    MinAgg,
    FoldFailuresOrder,
)

approaches: list[TcpApproach] = [
    BaseOrder(),
    RandomOrder(),
    CodeDistOrder(
        CodeXEmbed(slice=100), EuclidDist(), MinAgg(), fail_adapt=True, debug=True
    ),
    FoldFailuresOrder("dfe"),
    FoldFailuresOrder("total"),
    FoldFailuresOrder("recent"),
]

little_proxy = TcpDataset(
    runs_path="./datasets/adamfisk@LittleProxy.csv",
    repo_path="./datasets/LittleProxy",
    run_to_commit_path="./datasets/tr_all_built_commits.csv",
)
evaluate(approaches, little_proxy, debug=1)
del little_proxy

jade4j = TcpDataset(
    runs_path="./datasets/neuland@jade4j.csv",
    repo_path="./datasets/jade4j",
    run_to_commit_path="./datasets/tr_all_built_commits.csv",
)
evaluate(approaches, jade4j, debug=1)
del jade4j

achilles = TcpDataset(
    runs_path="./datasets/doanduyhai@Achilles.csv",
    repo_path="./datasets/Achilles",
    run_to_commit_path="./datasets/tr_all_built_commits.csv",
    subprojects=["achilles-core", "achilles-cql", "achilles-model", "achilles-thrift"],
)
evaluate(approaches, achilles, debug=1)
del achilles
