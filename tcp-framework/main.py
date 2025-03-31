from tcp_framework import (
    evaluate,
    TcpApproach,
    TcpDataset,
    CodeDistOrder,
    BaseOrder,
    RandomOrder,
    CodeXEmbed,
    CosSimDist,
    EuclidDist,
    MannDist,
    MinAgg,
    AvgAgg,
    MaxAgg,
)

little_proxy = TcpDataset(
    runs_path="../experiments/new-approach/adamfisk@LittleProxy.csv",
    repo_path="../experiments/new-approach/LittleProxy",
    run_to_commit_path="../experiments/new-approach/tr_all_built_commits.csv",
)

vectorizer = CodeXEmbed()

approaches: list[TcpApproach] = [
    BaseOrder(),
    RandomOrder(),
]

for dist in [CosSimDist(), EuclidDist(), MannDist()]:
    for agg in [MinAgg(), AvgAgg(), MaxAgg()]:
        for fail_adapt in [True, False]:
            approaches.append(CodeDistOrder(vectorizer, dist, agg, fail_adapt, debug=True))

evaluate(approaches, little_proxy, debug=True)
