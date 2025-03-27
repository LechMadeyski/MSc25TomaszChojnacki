from .approaches import TcpApproach
from .datatypes import RunContext, TestCase, TestResult
from .tcp_dataset import TcpDataset


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


def evaluate(approaches: list[TcpApproach], dataset: TcpDataset) -> None:
    apfds = [[] for _ in approaches]

    for run_id, test_cases in dataset.runs():
        if sum(tc["failures"] for tc in test_cases) == 0:
            continue  # TODO

        def inspect_code(target: TestCase) -> str:
            for tc in test_cases:
                if tc["testName"] == target.name:
                    return tc["content"]
            raise ValueError

        print(f"Run ID: {run_id}")

        for ai, approach in enumerate(approaches):
            result = []

            def execute(target: TestCase) -> TestResult:
                for tc in test_cases:
                    if tc["testName"] == target.name:
                        if tc in result:
                            raise ValueError
                        result.append(tc)
                        return TestResult(failures=tc["failures"], duration_s=tc["duration"])
                raise ValueError

            ctx = RunContext(
                test_cases=[TestCase(name=tc["testName"]) for tc in test_cases],
                execute=execute,
                inspect_code=inspect_code,
            )
            approach.prioritize(ctx)
            if len(test_cases) != len(result):
                raise ValueError

            apfd = _metric_apfd([tc["failures"] for tc in result])
            apfds[ai].append(apfd)

        for ai, approach in enumerate(approaches):
            print(f"APFD_{ai}: {sum(apfds[ai]) / len(apfds[ai]):.3}, ", end="")
        print(flush=True)
