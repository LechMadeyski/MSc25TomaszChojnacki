from tcp_framework import (
    evaluate,
    TcpDataset,
    Proposed,
    BaseOrder,
    RandomOrder,
    CodeXEmbed,
    CosSimDist,
    EuclidDist,
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

evaluate(
    [
        BaseOrder(),
        RandomOrder(),
        Proposed(vectorizer, CosSimDist(), MinAgg()),
        Proposed(vectorizer, CosSimDist(), AvgAgg()),
        Proposed(vectorizer, CosSimDist(), MaxAgg()),
        Proposed(vectorizer, EuclidDist(), MinAgg()),
        Proposed(vectorizer, EuclidDist(), AvgAgg()),
        Proposed(vectorizer, EuclidDist(), MaxAgg()),
    ],
    little_proxy,
)
