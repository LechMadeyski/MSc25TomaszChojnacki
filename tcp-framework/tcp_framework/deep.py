from typing import Any, Callable, Sequence


def flatten[T](xss: Sequence[Sequence[T]]) -> list[T]:
    return [x for xs in xss for x in xs]


def deepen[T](xs: Sequence[T]) -> list[list[T]]:
    return [[x] for x in xs]


def deep_len(xss: Sequence[Sequence[Any]]) -> int:
    return sum(len(xs) for xs in xss)


def deep_map[T, R](xss: Sequence[Sequence[T]], f: Callable[[T], R]) -> list[list[R]]:
    return [[f(x) for x in xs] for xs in xss]


def deep_any[T](xss: Sequence[Sequence[T]], f: Callable[[T], bool]) -> bool:
    return any(f(x) for xs in xss for x in xs)


def deep_remove[T](xss: list[list[T]], x: T) -> None:
    for xs in xss:
        if x in xs:
            xs.remove(x)
            if len(xs) == 0:
                xss.remove(xs)
            return
    raise ValueError
