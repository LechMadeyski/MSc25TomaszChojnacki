from tqdm import tqdm
from .approaches import Approach
from .datatypes import RunContext
from .dataset import Dataset


def _metric_apfd(fails: list[int]) -> float:
    n = len(fails)
    m = sum(fails)
    if m == 0:
        return float("nan")
    s = 0
    for i, f in enumerate(fails):
        s += (i + 1) * f
    return 1 - (s / (n * m)) + (1 / (2 * n))


def evaluate(approaches: list[Approach], dataset: Dataset, *, debug: int = 0) -> None:
    for approach in approaches:
        approach.reset()

    apfds: list[list[float]] = [[] for _ in approaches]

    cycles = dataset.cycles(debug=debug > 1)

    for cycle in tqdm(cycles, desc="evaluate", leave=False, disable=(debug != 1)):
        gather_metrics = len(cycle.tests) >= 5 and sum(ti.result.fails for ti in cycle.tests) > 0  # Bagherzadeh 2021

        if debug > 1 and gather_metrics:
            print(f"Job ID: {cycle.job_id}")

        for ai, approach in enumerate(approaches):
            ctx = RunContext(cycle.tests)
            approach.prioritize(ctx)
            ordering = ctx.prioritized_infos()
            approach.on_static_feedback(ordering)

            if gather_metrics:
                apfds[ai].append(_metric_apfd([ti.result.fails for ti in ordering]))

        if debug > 1 and gather_metrics:
            for ai, approach in enumerate(approaches):
                print(f"A{ai + 1}: {sum(apfds[ai]) / len(apfds[ai]):.3f}   ", end="")
            print(f"   {dataset.name}")

    if debug > 0:
        for ai, approach in enumerate(approaches):
            print(f"A{ai + 1}: {sum(apfds[ai]) / len(apfds[ai]):.3f}   ", end="")
        print(f"   {dataset.name}")
