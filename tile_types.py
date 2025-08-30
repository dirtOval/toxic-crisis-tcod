from typing import Tuple

import numpy as np
from random import randint

# dt is like a struct in C. our dt is: a 32 bit int, and 3 unsigned bytes x2
# for foreground and background color? i'm sure this will make sense later
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # this corresponds to a Unicode character
        ("fg", "3B"),
        ("bg", "3B"),
    ]
)

tile_dt = np.dtype(
    [
        ("walkable", np.bool),
        ("transparent", np.bool),
        ("dark", graphic_dt),
        ("light", graphic_dt),
    ]
)


def new_tile(
    *,  # enforce use of keywords? find out what this means
    # oh wait i think it means arguments must be paired w/
    # keywords. sick.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    # dark=(ord(' '),(255, 255, 255), (50, 50, 150)),
    # light=(ord(' '), (255, 255, 255), (200, 180, 50)),
    dark=(ord("."), (0, 0, 125), (0, 0, 0)),
    light=(ord("."), (25, 0, 150), (0, 0, 25)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    # dark=(ord(' '),(255, 255, 255), (0, 0, 100)),
    # light=(ord(' '), (255, 255, 255), (130, 110, 50)),
    dark=(ord("#"), (0, 100, 0), (0, 0, 0)),
    light=(ord("#"), (0, 225, 0), (0, 0, 0)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    # dark=(ord('>'), (0, 0, 100), (50, 50, 150)),
    # light=(ord('>'), (255, 255, 255), (200, 180, 150)),
    dark=(ord(" "), (255, 255, 255), (50, 50, 150)),
    light=(ord(" "), (255, 255, 255), (200, 180, 50)),
)


def random() -> new_tile:
    coin_flip = randint(0, 1)
    if coin_flip == 0:
        return floor
    else:
        return wall


# add glass? transparent, but not walkable

