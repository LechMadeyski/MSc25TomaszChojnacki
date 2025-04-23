from .datatypes import TestInfo, TestResult


class MetricCalc:
    @staticmethod
    def apfd(results: list[TestResult]) -> float:
        n = len(results)
        m = sum(tr.fails for tr in results)
        if n == 0 or m == 0:
            return float("nan")
        nom = sum(c_i * tr.fails for c_i, tr in enumerate(results, start=1))
        return 1 - (nom / (n * m)) + (1 / (2 * n))

    @staticmethod
    def r_apfd(results: list[TestResult]) -> float:
        worst = sorted(results, key=lambda tr: tr.fails)
        apfd_min = MetricCalc.apfd(worst)
        apfd_max = MetricCalc.apfd(list(reversed(worst)))
        apfd = MetricCalc.apfd(results)
        if apfd_min == apfd_max:
            return float("nan")
        return (apfd - apfd_min) / (apfd_max - apfd_min)

    @staticmethod
    def apfd_c(results: list[TestResult]) -> float:
        n = len(results)
        m = sum(tr.fails for tr in results)
        denom = m * sum(tr.time_s for tr in results)
        if denom == 0:
            return float("nan")

        def tf(f_i: int) -> int:
            count = 0
            for c_i, tr in enumerate(results, start=1):
                count += tr.fails
                if count >= f_i:
                    return c_i
            raise ValueError

        nom = 0.0
        for j in range(1, m + 1):
            tf_j = tf(j)
            for i in range(tf_j, n + 1):
                nom += results[i - 1].time_s
            nom -= 0.5 * results[tf_j - 1].time_s

        return nom / denom

    @staticmethod
    def r_apfd_c(results: list[TestResult]) -> float:
        worst = sorted(results, key=lambda tr: tr.fails / tr.time_s if tr.time_s > 0 else float("inf"))
        apfd_c_min = MetricCalc.apfd_c(worst)
        apfd_c_max = MetricCalc.apfd_c(list(reversed(worst)))
        apfd_c = MetricCalc.apfd_c(results)
        if apfd_c_min == apfd_c_max:
            return float("nan")
        return (apfd_c - apfd_c_min) / (apfd_c_max - apfd_c_min)

    @staticmethod
    def _avg(values: list[float]) -> float:
        if not values:
            return float("nan")
        return sum(values) / len(values)

    def __init__(self, min_cases: int = 1) -> None:
        self._min_cases = min_cases  # Bagherzadeh 2021
        self._all_apfd: list[float] = []
        self._all_r_apfd: list[float] = []
        self._all_apfd_c: list[float] = []
        self._all_r_apfd_c: list[float] = []

    def include(self, ordering: list[TestInfo]) -> None:
        results = [ti.result for ti in ordering]
        if len(results) < self._min_cases or sum(tr.fails for tr in results) == 0:
            return None

        self._all_apfd.append(self.apfd(results))
        self._all_r_apfd.append(self.r_apfd(results))
        self._all_apfd_c.append(self.apfd_c(results))
        self._all_r_apfd_c.append(self.r_apfd_c(results))

    @property
    def avg_apfd(self) -> float:
        return self._avg(self._all_apfd)

    @property
    def avg_r_apfd(self) -> float:
        return self._avg(self._all_r_apfd)

    @property
    def avg_apfd_c(self) -> float:
        return self._avg(self._all_apfd_c)

    @property
    def avg_r_apfd_c(self) -> float:
        return self._avg(self._all_r_apfd_c)
