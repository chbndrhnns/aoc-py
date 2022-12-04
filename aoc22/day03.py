import dataclasses
import typing as t
from itertools import islice
from pathlib import Path

import pytest

SMALL_CHAR_OFFSET = 96

CAPITAL_CHAR_OFFSET = 38


@dataclasses.dataclass
class Rucksack:
    one: str
    two: str
    common: set[str]

    @property
    def sum_of_priorities(self):
        return sum(self.priority_for_(item) for item in self.common)

    @classmethod
    def from_string(cls, val: str) -> t.Self:
        split_at = len(val) // 2
        one, two = val[:split_at], val[split_at:]
        common = {char for char in one if char in two}
        return cls(one=one, two=two, common=common)

    def priority_for_(self, val: str):
        if val not in self.common:
            raise ValueError(f"No common value: {val}")

        return _calculate_priority(val)

    def __hash__(self) -> int:
        return hash(self.one + self.two)

    def __iter__(self):
        yield from self.one + self.two


def _calculate_priority(val):
    offset = CAPITAL_CHAR_OFFSET if val.isupper() else SMALL_CHAR_OFFSET
    return ord(val) - offset


class Group(t.Sequence):
    def __init__(self, seq: t.Sequence = ()):
        assert len(seq) == 3, "Can only work with three rucksacks"
        self._rucksacks: list[Rucksack] = list(seq)

    @property
    def badge(self):
        shared = set.intersection(*[set(r) for r in self._rucksacks])
        return next(iter(shared))

    @property
    def priority(self):
        return _calculate_priority(self.badge)

    def __getitem__(self, index: int) -> Rucksack:
        return self._rucksacks[index]

    def __len__(self) -> int:
        return len(self._rucksacks)

    def __iter__(self):
        yield from self._rucksacks


@pytest.mark.parametrize(
    "val,one,two",
    [
        ("AaAb", "Aa", "Ab"),
        ("vJrwpWtwJgWrhcsFMMfFFhFp", "vJrwpWtwJgWr", "hcsFMMfFFhFp"),
    ],
)
def test_parse_into_rucksack(val, one, two):
    rucksack = Rucksack.from_string(val)
    assert rucksack.one == one
    assert rucksack.two == two


@pytest.mark.parametrize(
    "val,expected",
    [
        ("AaAb", {"A"}),
        ("vJrwpWtwJgWrhcsFMMfFFhFp", {"p"}),
    ],
)
def test_finds_common_parts(val, expected):
    rucksack = Rucksack.from_string(val)
    assert rucksack.common == expected


@pytest.mark.parametrize(
    "val, expected",
    [
        ("AA", 27),
        ("aa", 1),
    ],
)
def test_rucksack_computes_priority(val, expected):
    rucksack = Rucksack.from_string(val)
    assert rucksack.priority_for_(val[0]) == expected


@pytest.mark.parametrize(
    "val,expected",
    [
        ("AaAb", 27),
        ("vJrwpWtwJgWrhcsFMMfFFhFp", 16),
        ("jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL", 38),
        ("PmmdzqPrVvPwwTWBwg", 42),
        ("wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn", 22),
    ],
)
def test_sums_priorities(val, expected):
    rucksack = Rucksack.from_string(val)
    assert rucksack.sum_of_priorities == expected


@pytest.mark.parametrize(
    "group,badge",
    [
        (
            [
                "vJrwpWtwJgWrhcsFMMfFFhFp",
                "jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL",
                "PmmdzqPrVvPwwTWBwg",
            ],
            "r",
        ),
        (
            [
                "wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn",
                "ttgJtRGJQctTZtZT",
                "CrZsJsPPZsGzwwsLwLmpwMDw",
            ],
            "Z",
        ),
    ],
)
def test_find_badge(group, badge):
    group = Group([Rucksack.from_string(s) for s in group])
    assert group.badge == badge


@pytest.mark.parametrize(
    "group,priority",
    [
        (
            [
                "vJrwpWtwJgWrhcsFMMfFFhFp",
                "jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL",
                "PmmdzqPrVvPwwTWBwg",
            ],
            18,
        ),
        (
            [
                "wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn",
                "ttgJtRGJQctTZtZT",
                "CrZsJsPPZsGzwwsLwLmpwMDw",
            ],
            52,
        ),
    ],
)
def test_find_group_priority(group, priority):
    group = Group([Rucksack.from_string(s) for s in group])
    assert group.priority == priority


def test_sum_priorities():
    data = (Path(__file__).parent / "day03_input.txt").read_text()
    total = 0
    for val in data.strip().split("\n"):
        total += Rucksack.from_string(val).sum_of_priorities

    assert total == 8039


def test_group_priorities():
    data = (Path(__file__).parent / "day03_input.txt").read_text()
    as_lines = data.strip().split("\n")
    total = 0

    counter = 0
    while True:
        next_group = list(islice(as_lines, counter, counter + 3))
        if not next_group:
            break
        counter += 3
        group = Group(next_group)
        total += group.priority

    assert total == 2510
