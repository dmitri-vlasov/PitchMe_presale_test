from __future__ import annotations

from datetime import date
from operator import methodcaller
from typing import List

comparison_functions = {
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
    "==": lambda x, y: x == y,
}


def merge_intervals(intervals: List[List[date]]) -> List[List[date]]:
    """
    Merges time intervals to avoid counting overlapping experience.
    Used further to calculate years of non-overlapping experience of a candidate.
    """
    non_overlapping_intervals = [intervals[0]]

    for start, end in intervals[1:]:
        previous_end = non_overlapping_intervals[-1][1]

        if start <= previous_end:
            non_overlapping_intervals[-1][1] = max(previous_end, end)
        else:
            non_overlapping_intervals.append([start, end])

    return non_overlapping_intervals


class LowerCaseFrozenSet(frozenset):
    """
    Used to perform comparisons in lowercase
    """

    def __new__(cls, data):
        data = set(map(methodcaller('lower'), data))
        return super(LowerCaseFrozenSet, cls).__new__(cls, data)


def has_intersection_or_is_subset(
    set_to_evaluate: LowerCaseFrozenSet[str],
    required_set: LowerCaseFrozenSet[str],
    number_of_hits: int,
) -> bool:
    """
    Depending on number_of_hits determines if set_to_evaluate
    has intersection with or is subset of required_set
    """
    if number_of_hits:
        number_of_intersections = len(set_to_evaluate.intersection(required_set))
        return number_of_intersections == number_of_hits

    return required_set.issubset(set_to_evaluate)
