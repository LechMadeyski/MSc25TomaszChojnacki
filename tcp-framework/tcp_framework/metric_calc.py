from typing import Sequence

from .datatypes import TestInfo, TestResult
from .deep import deep_map

EPSILON = 1e-6


class MetricCalc:
    @staticmethod
    def apfd(results: Sequence[TestResult]) -> float:
        n = len(results)
        m = sum(tr.fails for tr in results)
        if n == 0 or m == 0:
            return float("nan")
        nom = sum(c_i * tr.fails for c_i, tr in enumerate(results, start=1))
        return 1 - (nom / (n * m)) + (1 / (2 * n))

    @staticmethod
    def r_apfd(results: Sequence[TestResult]) -> float:
        worst = sorted(results, key=lambda tr: tr.fails)
        apfd_min = MetricCalc.apfd(worst)
        apfd_max = MetricCalc.apfd(list(reversed(worst)))
        apfd = MetricCalc.apfd(results)
        if apfd_min == apfd_max:
            return float("nan")
        return (apfd - apfd_min) / (apfd_max - apfd_min)

    @staticmethod
    def apfd_c(results: Sequence[TestResult]) -> float:
        n = len(results)
        m = sum(tr.fails for tr in results)
        denom = m * sum(tr.time_s for tr in results)
        if denom < EPSILON:
            return float("nan")

        def tf(f_i: int) -> int:
            count = 0
            for c_i, tr in enumerate(results, start=1):
                count += tr.fails
                if count >= f_i:
                    return c_i
            raise ValueError("unreachable reached in apfd_c")

        nom = 0.0
        for j in range(1, m + 1):
            tf_j = tf(j)
            for i in range(tf_j, n + 1):
                nom += results[i - 1].time_s
            nom -= 0.5 * results[tf_j - 1].time_s

        return nom / denom

    @staticmethod
    def r_apfd_c(results: Sequence[TestResult]) -> float:
        worst = sorted(results, key=lambda tr: tr.fails / tr.time_s if tr.time_s > 0 else float("inf"))
        apfd_c_min = MetricCalc.apfd_c(worst)
        apfd_c_max = MetricCalc.apfd_c(list(reversed(worst)))
        apfd_c = MetricCalc.apfd_c(results)
        if apfd_c_min == apfd_c_max:
            return float("nan")
        return (apfd_c - apfd_c_min) / (apfd_c_max - apfd_c_min)

    @staticmethod
    def n_apfd(results: Sequence[TestResult], *, p: float) -> float:
        n = len(results)
        m = sum(tr.fails for tr in results)
        if n == 0 or m == 0:
            return float("nan")
        nom = sum(c_i * tr.fails for c_i, tr in enumerate(results, start=1))
        return p - (nom / (n * m)) + (p / (2 * n))

    @staticmethod
    def rpa(results: Sequence[TestResult]) -> float:
        k = len(results)
        optimal = sorted(results, key=lambda tr: (-abs(tr.fails), tr.time_s))
        nom = 0.0
        for ti, t in enumerate(results, start=1):
            for _ in range(ti, k + 1):  # ???
                nom += k - optimal.index(t) + 2
        return nom / (k * k * (k + 1) / 2)

    @staticmethod
    def _rpa_m(*, k: int) -> float:
        nom = 0.0
        for i in range(1, k):
            nom += (k - i) * (k - i + 1)
        return 1 - nom / (k * k * (k + 1))

    @staticmethod
    def nrpa(results: Sequence[TestResult]) -> float:
        return MetricCalc.rpa(results) / MetricCalc._rpa_m(k=len(results))

    @staticmethod
    def ntr(cycles: Sequence[list[TestResult]]) -> float:
        nom = 0.0
        denom = 0.0
        for cycle in cycles:
            if any(tr.fails > 0 for tr in cycle):
                nom += MetricCalc._ntr_nom(cycle)
                denom += MetricCalc._ntr_denom(cycle)
        return nom / denom if denom > 0 else float("nan")

    @staticmethod
    def _ntr_nom(results: Sequence[TestResult]) -> float:
        if not any(tr.fails > 0 for tr in results):
            return float("nan")
        total_time = sum(tr.time_s for tr in results)
        first_i = next(i for i, tr in enumerate(results) if tr.fails > 0)
        time_to_first = sum(tr.time_s for tr in results[: first_i + 1])
        return total_time - time_to_first

    @staticmethod
    def _ntr_denom(results: Sequence[TestResult]) -> float:
        if not any(tr.fails > 0 for tr in results):
            return float("nan")
        return sum(tr.time_s for tr in results)

    @staticmethod
    def _atr_cycle_time(results: Sequence[TestResult], *, build_time_s: float, tcp_time_s: float) -> float:
        first_i = next((i for i, tr in enumerate(results) if tr.fails > 0), len(results) - 1)
        return max(tcp_time_s - build_time_s, 0.0) + sum(tr.time_s for tr in results[: first_i + 1])

    @staticmethod
    def _avg(values: Sequence[float]) -> float:
        if not values:
            return float("nan")
        return sum(values) / len(values)

    def __init__(self, min_cases: int = 1) -> None:
        self._min_cases = min_cases  # Bagherzadeh 2021
        self._all_apfd: list[float] = []
        self._all_r_apfd: list[float] = []
        self._all_apfd_c: list[float] = []
        self._all_r_apfd_c: list[float] = []
        self._all_rpa: list[float] = []
        self._all_nrpa: list[float] = []
        self._ntr_nom_sum = 0.0
        self._ntr_denom_sum = 0.0
        self._atr_nom_sum = 0.0
        self._atr_denom_sum = 0.0

    def include_group(
        self,
        *,
        ordered_group: Sequence[Sequence[TestInfo]],
        base: Sequence[TestInfo],
        build_time_s: float,
        tcp_time_s_group: Sequence[float],
    ) -> None:
        assert len(ordered_group) == len(tcp_time_s_group), "results and times must have the same length"
        base_r = [ti.result for ti in base]
        ordered_r_group = deep_map(ordered_group, lambda ti: ti.result)
        if len(base_r) < self._min_cases:
            return

        self._all_rpa.append(self._avg([self.rpa(ordered_r) for ordered_r in ordered_r_group]))
        self._all_nrpa.append(self._avg([self.nrpa(ordered_r) for ordered_r in ordered_r_group]))
        self._atr_nom_sum += self._avg(
            [
                self._atr_cycle_time(ordered_r, build_time_s=build_time_s, tcp_time_s=tcp_time_s)
                for ordered_r, tcp_time_s in zip(ordered_r_group, tcp_time_s_group)
            ]
        )
        self._atr_denom_sum += self._atr_cycle_time(base_r, build_time_s=build_time_s, tcp_time_s=0.0)

        if not any(tr.fails > 0 for tr in base_r):
            return

        self._all_apfd.append(self._avg([self.apfd(ordered_r) for ordered_r in ordered_r_group]))
        self._all_r_apfd.append(self._avg([self.r_apfd(ordered_r) for ordered_r in ordered_r_group]))
        self._all_apfd_c.append(self._avg([self.apfd_c(ordered_r) for ordered_r in ordered_r_group]))
        self._all_r_apfd_c.append(self._avg([self.r_apfd_c(ordered_r) for ordered_r in ordered_r_group]))
        self._ntr_nom_sum += self._avg([self._ntr_nom(ordered_r) for ordered_r in ordered_r_group])
        self._ntr_denom_sum += self._avg([self._ntr_denom(ordered_r) for ordered_r in ordered_r_group])

    def include(
        self, *, ordered: Sequence[TestInfo], base: Sequence[TestInfo], build_time_s: float, tcp_time_s: float
    ) -> None:
        self.include_group(
            ordered_group=[ordered],
            base=base,
            build_time_s=build_time_s,
            tcp_time_s_group=[tcp_time_s],
        )

    @property
    def failed_cycles(self) -> int:
        return len(self._all_apfd)

    @property
    def apfd_avg(self) -> float:
        return self._avg(self._all_apfd)

    @property
    def apfd_list(self) -> list[float]:
        return self._all_apfd

    @property
    def r_apfd_avg(self) -> float:
        return self._avg(self._all_r_apfd)

    @property
    def r_apfd_list(self) -> list[float]:
        return self._all_r_apfd

    @property
    def apfd_c_avg(self) -> float:
        return self._avg(self._all_apfd_c)

    @property
    def apfd_c_list(self) -> list[float]:
        return self._all_apfd_c

    @property
    def r_apfd_c_avg(self) -> float:
        return self._avg(self._all_r_apfd_c)

    @property
    def r_apfd_c_list(self) -> list[float]:
        return self._all_r_apfd_c

    @property
    def rpa_avg(self) -> float:
        return self._avg(self._all_rpa)

    @property
    def rpa_list(self) -> list[float]:
        return self._all_rpa

    @property
    def nrpa_avg(self) -> float:
        return self._avg(self._all_nrpa)

    @property
    def nrpa_list(self) -> list[float]:
        return self._all_nrpa

    @property
    def ntr_val(self) -> float:
        return self._ntr_nom_sum / self._ntr_denom_sum if self._ntr_denom_sum > 0 else float("nan")

    @property
    def atr_val(self) -> float:
        return 1 - (self._atr_nom_sum / self._atr_denom_sum) if self._atr_denom_sum > 0 else float("nan")

    @property
    def atr_approach_total_s(self) -> float:
        return self._atr_nom_sum

    @property
    def atr_base_total_s(self) -> float:
        return self._atr_denom_sum
