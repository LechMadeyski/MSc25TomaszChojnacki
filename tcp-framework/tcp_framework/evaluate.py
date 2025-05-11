import time
from typing import Literal, Optional, Sequence

from tqdm import tqdm

from .approaches import Approach
from .dataset import Dataset
from .datatypes import RunContext
from .deep import flatten
from .metric_calc import MetricCalc

type SupportedMetric = Literal["APFD", "rAPFD", "APFDc", "rAPFDc", "RPA", "NRPA", "NTR", "ATR"]


def _print_metrics(calcs: Sequence[MetricCalc], metrics: Sequence[SupportedMetric], trailer: str = "") -> None:
    for mi, metric in enumerate(metrics):
        for ci, calc in enumerate(calcs, start=1):
            match metric:
                case "APFD":
                    print(f"A{ci}: {calc.apfd_avg:.3f}   ", end="")
                case "rAPFD":
                    print(f"a{ci}: {calc.r_apfd_avg:.3f}   ", end="")
                case "APFDc":
                    print(f"C{ci}: {calc.apfd_c_avg:.3f}   ", end="")
                case "rAPFDc":
                    print(f"c{ci}: {calc.r_apfd_c_avg:.3f}   ", end="")
                case "RPA":
                    print(f"R{ci}: {calc.rpa_avg:.3f}   ", end="")
                case "NRPA":
                    print(f"r{ci}: {calc.nrpa_avg:.3f}   ", end="")
                case "NTR":
                    print(f"N{ci}: {calc.ntr_val:.3f}   ", end="")
                case "ATR":
                    print(f"n{ci}:{calc.atr_val:+.3f}   ", end="")
                case _:
                    raise ValueError(f"unsupported metric: {metric}")
        if mi == 0:
            trailer = f"   {trailer} [{calc.failed_cycles}]" if trailer else f"   [{calc.failed_cycles}]"
            print(trailer)
        else:
            print()


def evaluate(
    approaches: Sequence[Approach],
    dataset: Dataset,
    metrics: Optional[Sequence[SupportedMetric]] = None,
    *,
    debug: int = 0,
) -> list[MetricCalc]:
    if not metrics:
        metrics = []
    for approach in approaches:
        approach.reset()

    calcs = [MetricCalc(min_cases=6) for _ in approaches]

    cycles = dataset.cycles(debug=debug > 1)

    for cycle in tqdm(cycles, desc="evaluate", leave=False, disable=(debug != 1)):
        for ai, approach in enumerate(approaches):
            ctx = RunContext(cycle.tests)
            start = time.monotonic()
            approach.prioritize(ctx)
            end = time.monotonic()
            ordering = flatten(ctx.prioritized_infos())
            approach.on_static_feedback(ordering)
            calcs[ai].include(
                ordered=ordering, base=cycle.tests, build_time_s=cycle.build_time_s, tcp_time_s=end - start
            )

        if debug > 1:
            _print_metrics(calcs, metrics, trailer=f"#{cycle.job_id}")

    if debug > 0:
        _print_metrics(calcs, metrics, trailer=dataset.name)

    return calcs
