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
)

little_proxy = TcpDataset(
    runs_path="../experiments/new-approach/adamfisk@LittleProxy.csv",
    repo_path="../experiments/new-approach/LittleProxy",
    run_to_commit_path="../experiments/new-approach/tr_all_built_commits.csv",
)

approaches: list[TcpApproach] = [
    BaseOrder(),
    RandomOrder(),
    CodeDistOrder(CodeXEmbed(), EuclidDist(), MinAgg(), fail_adapt=True, debug=True),
]

evaluate(approaches, little_proxy, debug=True)
