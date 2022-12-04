import dataclasses
from pathlib import Path

import pytest


@dataclasses.dataclass
class Section:
    start: int
    end: int

    @property
    def range(self):
        return set(range(self.start, self.end + 1))

    @classmethod
    def from_str(cls, val):
        start, end = val.split("-")
        return cls(start=int(start), end=int(end))


@dataclasses.dataclass
class Pair:
    one: Section
    other: Section

    @property
    def has_full_overlap(self):
        return (
            self.one.range.intersection(self.other.range) == self.one.range
            or self.other.range.intersection(self.one.range) == self.other.range
        )

    @property
    def has_partial_overlap(self):
        return bool(
            self.one.range.intersection(self.other.range)
            or self.other.range.intersection(self.one.range)
        )

    @classmethod
    def from_str(cls, val: str):
        one, other = [Section.from_str(section) for section in val.split(",")]
        return cls(one=one, other=other)


def test_can_create_section():
    s = Section.from_str("2-4")
    assert s.start == 2
    assert s.end == 4
    assert s.range == {2, 3, 4}


def test_can_parse_pair():
    pair = Pair.from_str("2-4,6-8")
    assert pair.one.range == {2, 3, 4}
    assert pair.other.range == {6, 7, 8}


@pytest.mark.parametrize(
    "pair,result",
    [
        ("2-4,6-8", False),
        ("2-8,3-7", True),
    ],
)
def test_find_full_overlap(pair, result):
    assert Pair.from_str(pair).has_full_overlap == result


@pytest.mark.parametrize(
    "pair,result",
    [
        ("2-4,6-8", False),
        ("2-8,3-7", True),
        ("2-6,4-8", True),
    ],
)
def test_find_partial_overlap(pair, result):
    assert Pair.from_str(pair).has_partial_overlap == result


def test_part_01():
    data = (Path(__file__).parent / "day04_input.txt").read_text()
    total = 0
    for val in data.strip().split("\n"):
        total += int(Pair.from_str(val).has_full_overlap)

    assert total == 464


def test_part_02():
    data = (Path(__file__).parent / "day04_input.txt").read_text()
    total = 0
    for val in data.strip().split("\n"):
        total += int(Pair.from_str(val).has_partial_overlap)

    assert total == 770
