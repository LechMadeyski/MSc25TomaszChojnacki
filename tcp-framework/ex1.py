from pathlib import Path

from tcp_framework import Dataset, evaluate, metric_boxplot
from tcp_framework.approaches import Approach, CodeDistOrder, RandomOrder
from tcp_framework.approaches.representation import StVectorizer

REPOS = [
    "LittleProxy",
    "HikariCP",
    "jade4j",
    "wicket-bootstrap",
    "titan",
    "dynjs",
    "jsprit",
    "DSpace",
    "optiq",
    "cloudify",
    "okhttp",
]

APPROACHES: list[Approach] = [
    RandomOrder(),
    CodeDistOrder(StVectorizer("Salesforce/SFR-Embedding-Code-400M_R")),
    CodeDistOrder(StVectorizer("intfloat/e5-base-v2")),
    CodeDistOrder(StVectorizer("BAAI/bge-base-en-v1.5")),
    CodeDistOrder(StVectorizer("microsoft/unixcoder-base")),
]

if __name__ == "__main__":
    cycle_map = Dataset.preload_cycle_map(Path("./datasets/travistorrent_8_2_2017.csv"), debug=True)

    datasets = [
        Dataset(cycles_path=Path(f"./datasets/{repo}.csv"), repo_path=Path(f"./datasets/{repo}"), cycle_map=cycle_map)
        for repo in REPOS
    ]

    for dataset in datasets:
        calcs = evaluate(APPROACHES, dataset, ["ATR"], debug=1)
        metric_boxplot(
            f"./out/ex1-rAPFD-{dataset.name}.pdf",
            [c.r_apfd_list for c in calcs],
            title=f"rAPFD - {dataset.name}",
            labels=["Random", "CodeXEmbed", "E5", "BGE", "UniXCoder"],
        )
