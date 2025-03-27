from tcp_framework import evaluate, TcpDataset, Proposed, BaseOrder, RandomOrder
from tcp_framework.vectorizers import CodeXEmbed

little_proxy = TcpDataset(
    runs_path="../experiments/new-approach/adamfisk@LittleProxy.csv",
    repo_path="../experiments/new-approach/LittleProxy",
    run_to_commit_path="../experiments/new-approach/tr_all_built_commits.csv",
)

evaluate([BaseOrder(), RandomOrder(), Proposed(CodeXEmbed())], little_proxy)
