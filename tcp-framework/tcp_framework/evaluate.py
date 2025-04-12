from collections import Counter
from tqdm import tqdm
from .approaches import Approach
from .datatypes import RunContext, TestCase, TestInfo, TestResult
from .dataset import Dataset


def _metric_apfd(failures: list[int]) -> float:
    n = len(failures)
    m = sum(failures)
    if m == 0:
        return float("nan")
    s = 0
    for i, f in enumerate(failures):
        for _ in range(f):
            s += i + 1
    return 1 - (s / (n * m)) + (1 / (2 * n))


def evaluate(approaches: list[Approach], dataset: Dataset, *, debug: int = 0) -> None:
    for approach in approaches:
        approach.reset()

    apfds: list[list[float]] = [[] for _ in approaches]

    for run_id, test_infos in tqdm(dataset.runs(), leave=False, disable=(debug != 1)):
        gather_metrics = sum(ti.failures for ti in test_infos) > 0

        if debug > 1 and gather_metrics:
            print(f"Run ID: {run_id}")

        def inspect_code(target: TestCase) -> str:
            for ti in test_infos:
                if ti.name == target.name:
                    return ti.content
            raise ValueError

        for ai, approach in enumerate(approaches):
            result: list[TestInfo] = []

            def execute(target: TestCase) -> TestResult:
                for ti in test_infos:
                    if ti.name == target.name:
                        result.append(ti)
                        return ti.to_result()
                raise ValueError

            ctx = RunContext(
                test_cases=[ti.to_case() for ti in test_infos],
                execute=execute,
                inspect_code=inspect_code,
            )
            approach.prioritize(ctx)
            if Counter(tc.name for tc in test_infos) != Counter(
                tc.name for tc in result
            ):
                raise ValueError

            if gather_metrics:
                apfds[ai].append(_metric_apfd([ti.failures for ti in result]))

        if debug > 1 and gather_metrics:
            for ai, approach in enumerate(approaches):
                print(f"A{ai}: {sum(apfds[ai]) / len(apfds[ai]):.3f}   ", end="")
            print()

    if debug > 0:
        for ai, approach in enumerate(approaches):
            print(f"A{ai}: {sum(apfds[ai]) / len(apfds[ai]):.3f}   ", end="")
        print()
