import dataclasses
import typing as t
from enum import Enum
from pathlib import Path

import pytest

ROUND_INCREMENT = 1

POINTS_DRAW = 3

POINTS_WIN = 6


@dataclasses.dataclass
class Shape:
    score: t.ClassVar[int] = 0
    defeats: t.ClassVar[tuple] = ()

    @classmethod
    def wins_over(cls, other: t.Type["Shape"]):
        return other.__name__ in cls.defeats

    @classmethod
    def find_stronger_shape(cls):
        return [
            shape
            for shape in Shape.__subclasses__()
            if cls.__name__ in shape.defeats and shape.__name__ != cls.__name__
        ][0]

    @classmethod
    def decode(cls, val) -> t.Type["Shape"]:
        try:
            return DECODER_STRATEGY[val]
        except KeyError:
            raise ValueError(f"Could not decode '{val}")


class Paper(Shape):
    score: t.ClassVar[int] = 2
    defeats: t.ClassVar[tuple] = ("Rock",)


class Scissors(Shape):
    score: t.ClassVar[int] = 3
    defeats: t.ClassVar[tuple] = ("Paper",)


class Rock(Shape):
    score: t.ClassVar[int] = 1
    defeats: t.ClassVar[tuple] = ("Scissors",)


DECODER_STRATEGY = {
    "A": Rock,
    "B": Paper,
    "C": Scissors,
    "X": Rock,
    "Y": Paper,
    "Z": Scissors,
}


class Strategy(Enum):
    LOSE = "X"
    DRAW = "Y"
    WIN = "Z"


def decode_own_as_shape(other_val, my_val) -> t.Tuple[t.Type[Shape], t.Type[Shape]]:
    return Shape.decode(other_val), Shape.decode(my_val)


def decode_own_as_strategy(
    other_val: str, my_val: str
) -> t.Tuple[t.Type[Shape], t.Type[Shape]]:
    other = Shape.decode(other_val)

    if my_val == Strategy.WIN.value:
        own = other.find_stronger_shape()
    elif my_val == Strategy.LOSE.value:
        own = Shape.decode(other_val)
        own = [
            shape
            for shape in Shape.__subclasses__()
            if shape.__name__ == own.defeats[0]
        ][0]
    else:
        own = other

    return other, own


class Game:
    def __init__(self) -> None:
        self.my_score = 0
        self.other_score = 0
        self.rounds = 0
        self.my_last_shape = None
        self.other_last_shape = None

    def play_from_string(self, val: str, *, decoder=decode_own_as_shape):
        other_val, my_val = val.split(" ")
        other_shape, my_shape = decoder(other_val, my_val)
        self.play(my_shape, other_shape)

    def play(self, my_shape: t.Type[Shape], other_shape: t.Type[Shape]):
        self.my_last_shape = my_shape
        self.other_last_shape = other_shape

        self.my_score += my_shape.score
        self.other_score += other_shape.score

        if my_shape == other_shape:
            self.my_score += POINTS_DRAW
            self.other_score += POINTS_DRAW
        elif my_shape.wins_over(other_shape):
            self.my_score += POINTS_WIN
        else:
            self.other_score += POINTS_WIN

        self.rounds += ROUND_INCREMENT


@pytest.mark.parametrize(
    "encoded,shape",
    [
        ("A", Rock),
        ("X", Rock),
        ("B", Paper),
        ("Y", Paper),
        ("C", Scissors),
        ("Z", Scissors),
    ],
)
def test_can_decode(encoded, shape):
    assert Shape.decode(encoded) == shape


def test_can_decode_both_values_as_shapes():
    other, own = decode_own_as_shape("A", "Z")
    assert other == Rock
    assert own == Scissors


@pytest.mark.parametrize(
    "other_val, own_val, expected",
    [
        ("A", "Z", Paper),
        ("A", "Y", Rock),
        ("C", "Z", Rock),
        ("B", "X", Rock),
    ],
)
def test_can_decode_own_as_strategy(other_val, own_val, expected):
    other, own = decode_own_as_strategy(other_val, own_val)
    assert own == expected


@pytest.mark.parametrize(
    "shape1,shape2",
    [
        (Rock, Scissors),
        (Scissors, Paper),
        (Paper, Rock),
    ],
)
def test_wins(shape1, shape2):
    assert shape1.wins_over(shape2)


@pytest.mark.parametrize(
    "shape1,shape2",
    [
        (Rock, Rock),
        (Paper, Paper),
        (Scissors, Scissors),
    ],
)
def test_draw(shape1, shape2):
    assert shape1 == shape2


@pytest.mark.parametrize(
    "inp,my_score,other_score",
    [
        ((Rock, Rock), 4, 4),
        ((Paper, Rock), 8, 1),
        ((Scissors, Rock), 3, 7),
    ],
)
def test_counts_score(inp, my_score, other_score):
    game = Game()
    game.play(*inp)
    assert game.other_score == other_score
    assert game.my_score == my_score


@pytest.mark.parametrize(
    "inp,my_score",
    [
        ("A Y", 8),
        ("B X", 1),
        ("C Z", 6),
    ],
)
def test_can_score_round(inp, my_score):
    game = Game()
    game.play_from_string(inp)
    assert game.my_score == my_score


def test_can_score_dummy_game():
    game = Game()
    test_data = """
A Y
B X
C Z
    """

    for val in test_data.strip().split("\n"):
        game.play_from_string(val)

    assert game.rounds == 3
    assert game.my_score == 15
    assert game.other_score == 15


def test_can_score_game():
    data = (Path(__file__).parent / "day02_input.txt").read_text()
    game = Game()
    for val in data.strip().split("\n"):
        game.play_from_string(val)

    assert game.rounds == 2500
    assert game.my_score == 14531


def test_can_score_game_with_strategy():
    data = (Path(__file__).parent / "day02_input.txt").read_text()
    game = Game()
    for val in data.strip().split("\n"):
        game.play_from_string(val, decoder=decode_own_as_strategy)

    assert game.rounds == 2500
    assert game.my_score == 11258
