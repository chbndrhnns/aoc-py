import dataclasses
import typing as t
from pathlib import Path

import pytest


def get_max(elves):
    return max(elves, key=lambda x: x.carries)


def get_top_three(elves):
    return sorted(elves, key=lambda x: x.carries, reverse=True)[:3]


@dataclasses.dataclass
class Elf:
    carries: int


class Elves(t.Sequence):
    def __init__(self, seq: t.Iterable[Elf] = ()):
        self._elves = list(seq)

    def __getitem__(self, index: int):
        return self._elves[index]

    def __len__(self) -> int:
        return len(self._elves)

    def query_scalar(self, fn: t.Callable) -> Elf:
        return fn(self)

    def query(self, fn: t.Callable) -> t.List[Elf]:
        return fn(self)


class ElvesParser:
    def parse(self, data: str) -> Elves:
        elves = []
        for elf_data in data.split("\n\n"):
            elf = Elf(carries=sum(int(val) for val in elf_data.splitlines()))
            elves.append(elf)
        return Elves(elves)


@pytest.fixture
def data():
    return """1000
2000
3000

4000

5000
6000

7000
8000
9000

10000"""


def test_parse_calories(data):
    parser = ElvesParser()
    assert parser.parse(data)


def test_creates_elf(data):
    elves = ElvesParser().parse(data)
    assert elves[0].carries == 6000


def test_find_elf_that_carries_max_calories(data):
    elves = ElvesParser().parse(data)
    actual = elves.query_scalar(get_max)
    assert actual.carries == 24000


def test_find_top_three(data):
    elves = ElvesParser().parse(data)
    actual = elves.query(get_top_three)
    assert sum(elf.carries for elf in actual) == 45000


if __name__ == "__main__":
    data = (Path(__file__).parent / "day01_input.txt").read_text()
    elves = ElvesParser().parse(data)
    print(elves.query_scalar(get_max))
    print(sum(elf.carries for elf in elves.query(get_top_three)))
