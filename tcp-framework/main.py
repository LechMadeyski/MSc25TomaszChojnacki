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
    FoldFailuresOrder
)

little_proxy = TcpDataset(
    runs_path="./datasets/adamfisk@LittleProxy.csv",
    repo_path="./datasets/LittleProxy",
    run_to_commit_path="./datasets/tr_all_built_commits.csv",
)

approaches: list[TcpApproach] = [
    BaseOrder(),
    RandomOrder(),
    CodeDistOrder(CodeXEmbed(slice=100), EuclidDist(), MinAgg(), fail_adapt=True, debug=True),
    FoldFailuresOrder("dfe"),
    FoldFailuresOrder("total"),
    FoldFailuresOrder("recent"),
]

evaluate(approaches, little_proxy, debug=True)
