from collections import defaultdict, deque
from collections.abc import Iterable, Sequence
from typing import Literal, override

from ...datatypes import RunContext, TestCase, TestInfo
from ..approach import Approach

type _S = Iterable[TestCase]
type _FS = Literal[-1, 1]  # -1 for fail, 1 for pass
type _MF = dict[tuple[int, TestCase], _FS]
type _PS = dict[TestCase, int]

EPSILON = 1e-6


class RocketOrder(Approach):
    """
    Original: https://doi.org/10.1109/icsm.2013.91
    """

    def __init__(self, m: int = 1000, *, alpha_exe: float = 0.4) -> None:
        assert m > 0, "m must be a positive integer"
        assert 0.0 <= alpha_exe <= 1.0, "alpha_exe must be in the range [0, 1]"

        self._m = m
        self._alpha_exe = alpha_exe

        self._fs: defaultdict[TestCase, deque[_FS]] = defaultdict(lambda: deque(maxlen=m))
        self._exe_s: defaultdict[TestCase, float] = defaultdict(float)

    @override
    def prioritize(self, ctx: RunContext) -> None:
        s = ctx.test_cases
        mf = self._build_mf(s)
        ps = self._rankify(self._build_ps(s, mf))
        p = self._build_p(s, ps)
        for tc in sorted(s, key=lambda tc: p[tc]):
            ctx.execute(tc, key=f"{p[tc]:.3f}")

    @override
    def on_static_feedback(self, test_infos: Sequence[TestInfo]) -> None:
        for ti in test_infos:
            self._fs[ti.case].append(self._fs_val(ti))
            self._exe_s[ti.case] = self._alpha_exe * ti.result.time_s + (1.0 - self._alpha_exe) * self._exe_s[ti.case]

    @override
    def reset(self) -> None:
        self._fs.clear()
        self._exe_s.clear()

    def _build_mf(self, s: _S) -> _MF:
        return {(i, tc): self._fs[tc][-i] for tc in s for i in range(1, min(self._m, len(self._fs[tc])) + 1)}

    def _build_ps(self, s: _S, mf: _MF) -> _PS:
        return {tc: sum(mf[i, tc] * self._w(i) for i in range(1, min(self._m, len(self._fs[tc])) + 1)) for tc in s}

    def _build_p(self, s: _S, ps: _PS) -> dict[TestCase, float]:
        t_max_s = sum(self._exe_s[tc] for tc in s)
        if t_max_s < EPSILON:
            t_max_s = 1.0
        return {tc: ps[tc] + self._exe_s[tc] / t_max_s for tc in s}

    @classmethod
    def _fs_val(cls, ti: TestInfo) -> _FS:
        return -1 if ti.result.fails > 0 else 1

    @classmethod
    def _w(cls, i: int) -> int:
        assert i >= 1, "index must be a positive integer"
        match i:
            case 1:
                return 7
            case 2:
                return 2
            case _:
                return 1

    @classmethod
    def _rankify(cls, ps: dict[TestCase, int]) -> dict[TestCase, int]:
        order = sorted(set(ps.values()))
        ranks = {v: i for i, v in enumerate(order, start=1)}
        return {tc: ranks[ps[tc]] for tc in ps}
