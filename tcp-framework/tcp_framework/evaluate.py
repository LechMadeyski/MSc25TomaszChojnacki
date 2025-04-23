from typing import Literal
from tqdm import tqdm
from .approaches import Approach
from .datatypes import RunContext
from .dataset import Dataset
from .metric_calc import MetricCalc

type SupportedMetric = Literal["APFD", "rAPFD", "APFDc", "rAPFDc"]

def _print_metrics(calcs: list[MetricCalc], metrics: list[SupportedMetric], trailer: str = "") -> None:
    for mi, metric in enumerate(metrics):
        for ci, calc in enumerate(calcs, start=1):
            match metric:
                case "APFD":
                    print(f"A{ci}: {calc.avg_apfd:.3f}   ", end="")
                case "rAPFD":
                    print(f"a{ci}: {calc.avg_r_apfd:.3f}   ", end="")
                case "APFDc":
                    print(f"C{ci}: {calc.avg_apfd_c:.3f}   ", end="")
                case "rAPFDc":
                    print(f"c{ci}: {calc.avg_r_apfd_c:.3f}   ", end="")
        if trailer and mi == 0:
            print(f"   {trailer}")
        else:
            print()


def evaluate(approaches: list[Approach], dataset: Dataset, metrics: list[SupportedMetric], *, debug: int = 0) -> None:
    for approach in approaches:
        approach.reset()

    calcs = [MetricCalc(min_cases=5) for _ in approaches]

    cycles = dataset.cycles(debug=debug > 1)

    for cycle in tqdm(cycles, desc="evaluate", leave=False, disable=(debug != 1)):
        for ai, approach in enumerate(approaches):
            ctx = RunContext(cycle.tests)
            approach.prioritize(ctx)
            ordering = ctx.prioritized_infos()
            approach.on_static_feedback(ordering)
            calcs[ai].include(ordering)

        if debug > 1:
            _print_metrics(calcs, metrics, trailer=cycle.name)

    if debug > 0:
        _print_metrics(calcs, metrics, trailer=dataset.name)
