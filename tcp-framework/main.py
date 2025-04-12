from tcp_framework import (
    evaluate,
    Approach,
    Dataset,
    RandomOrder,
    FoldFailuresOrder,
    BaseOrder,
    TestLocOrder,
)

# vectorizer = CodeXEmbed(slice=100)

approaches: list[Approach] = [
    BaseOrder(),
    RandomOrder(),
    FoldFailuresOrder("dfe"),
    TestLocOrder(),
    # CodeDistOrder(vectorizer, EuclidDist(), MinAgg(), fail_adapt=3),
    # FaultCodeDistOrder(vectorizer, EuclidDist(), MinAgg()),
]

little_proxy = Dataset(
    runs_path="./datasets/adamfisk@LittleProxy.csv",
    repo_path="./datasets/LittleProxy",
    run_to_commit_path="./datasets/tr_all_built_commits.csv",
)
evaluate(approaches, little_proxy, debug=1)
del little_proxy

jade4j = Dataset(
    runs_path="./datasets/neuland@jade4j.csv",
    repo_path="./datasets/jade4j",
    run_to_commit_path="./datasets/tr_all_built_commits.csv",
)
evaluate(approaches, jade4j, debug=1)
del jade4j

achilles = Dataset(
    runs_path="./datasets/doanduyhai@Achilles.csv",
    repo_path="./datasets/Achilles",
    run_to_commit_path="./datasets/tr_all_built_commits.csv",
)
evaluate(approaches, achilles, debug=1)
del achilles
