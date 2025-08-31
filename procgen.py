from __future__ import annotations

from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING
import random
import numpy as np

import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

import tcod

import entity_factories
from game_map import GameMap

max_items_by_floor = [
    (1, 1),
    (4, 2),
]

max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

# item_chances: Dict[int, List[Tuple[Entity, int]]] = {
#  0: [(entity_factories.health_potion, 35)],
#  2: [(entity_factories.confusion_scroll, 10)],
#  4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
#  6: [(entity_factories.fireball_scroll, 25), (entity_factories.chain_mail, 15)],
# }
#
# enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
#  0: [(entity_factories.orc, 80)],
#  3: [(entity_factories.troll, 15)],
#  5: [(entity_factories.troll, 30)],
#  7: [(entity_factories.troll, 60)],
# }


def get_max_value_for_floor(
    max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value
        return current_value


def get_entities_at_random(
    weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property  # returns the area of the room in indices? play w this to understand
    def inner(self) -> Tuple[slice, slice]:
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def place_entities(
    room: RectangularRoom,
    dungeon: GameMap,
    entity: Entity,
    number_of_entities: int,
    # floor_number: int,
) -> None:
    # number_of_monsters = random.randint(
    #     0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    # )
    # number_of_items = random.randint(
    #     0, get_max_value_for_floor(max_items_by_floor, floor_number)
    # )

    # monsters: List[Entity] = get_entities_at_random(
    #     enemy_chances, number_of_monsters, floor_number
    # )
    # items: List[Entity] = get_entities_at_random(
    #     item_chances, number_of_items, floor_number
    # )

    # for i in range(number_of_monsters):
    #   x = random.randint(room.x1 + 1, room.x2 - 1)
    #   y = random.randint(room.y1 + 1, room.y2 - 1)

    #   if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
    #     if random.random() < 0.8:
    #       entity_factories.orc.spawn(dungeon, x, y)
    #     else:
    #       entity_factories.troll.spawn(dungeon, x, y)
    # for i in range(number_of_items):
    # for entity in monsters + items:
    for mob in range(number_of_entities):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            # entity_factories.health_potion.spawn(dungeon, x, y)
            # item_chance = random.random()

            # if item_chance < 0.7:
            #   entity_factories.health_potion.spawn(dungeon, x, y)
            # elif item_chance < 0.8:
            #   entity_factories.fireball_scroll.spawn(dungeon, x, y)
            # elif item_chance < 0.9:
            #   entity_factories.confusion_scroll.spawn(dungeon, x, y)
            # else:
            #   entity_factories.lightning_scroll.spawn(dungeon, x, y)
            entity.spawn(dungeon, x, y)


def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    x1, y1 = start
    x2, y2 = end

    # decides randomly whether to go horizontal then vertical or vice versa
    if random.random() < 0.5:
        corner_x, corner_y = x2, y1
    else:
        corner_x, corner_y = x1, y2

    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


# test dungeon not needed
# def generate_dungeon(map_width, map_height) -> GameMap:
# dungeon = GameMap(map_width, map_height)

# room_1 = RectangularRoom(x=20, y=15, width=10, height=15)
# room_2 = RectangularRoom(x=35, y=15, width=10, height=15)

# dungeon.tiles[room_1.inner] = tile_types.floor
# dungeon.tiles[room_2.inner] = tile_types.floor

# for x, y in tunnel_between(room_2.center, room_1.center):
#   dungeon.tiles[x, y] = tile_types.floor

# return dungeon


def summon_cops(dungeon: GameMap, amount: int) -> None:
    for cop in range(amount):
        x = random.randint(1, dungeon.width - 1)
        y = random.randint(1, dungeon.height - 1)
        if dungeon.get_blocking_entity_at_location(x, y):
            print("wall in way, cop skipped")
            continue
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity_factories.cop.spawn(dungeon, x, y)


def generate_crystals(dungeon: GameMap, amount: int) -> None:
    for crystal in range(amount):
        x = random.randint(1, dungeon.width - 1)
        y = random.randint(1, dungeon.height - 1)
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity_factories.crystal_well.spawn(dungeon, x, y)


def test_level(  # for testing new mechanics, mobs, etc
    map_width: int, map_height: int, engine: Engine
) -> GameMap:
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    room = RectangularRoom(1, 1, map_width - 2, map_height - 2)
    with np.nditer(dungeon.tiles[room.inner], op_flags=["readwrite"]) as zone:
        for tile in zone:
            cointoss = random.randint(0, 2)
            if cointoss == 0:
                tile[...] = tile_types.wall
            else:
                tile[...] = tile_types.floor

    # for i in np.ndindex(dungeon.tiles.shape):

    player.place(*room.center, dungeon)
    # generate_crystals(dungeon, 12)

    # entity_factories.crystal_well.spawn(dungeon, 35, 25)
    # entity_factories.miner.spawn(dungeon, 40, 25)
    # entity_factories.guard_eco_spawner.spawn(dungeon, 45, 25)

    # epic 4 way battle lmao
    # entity_factories.virus_spawner.spawn(dungeon, 20, 2)
    # entity_factories.virus_spawner.spawn(dungeon, 20, 41)
    # entity_factories.guard_spawner.spawn(dungeon, 60, 2)
    # entity_factories.guard_spawner.spawn(dungeon, 60, 41)

    return dungeon


def toxic_crisis_level(
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    room = RectangularRoom(1, 1, map_width - 2, map_height - 2)
    with np.nditer(dungeon.tiles[room.inner], op_flags=["readwrite"]) as zone:
        for tile in zone:
            cointoss = random.randint(0, 2)
            if cointoss == 0:
                tile[...] = tile_types.wall
            else:
                tile[...] = tile_types.floor

    player.place(*room.center, dungeon)
    place_entities(room, dungeon, entity_factories.snake, random.randint(1, 20))
    place_entities(room, dungeon, entity_factories.beef_snake, random.randint(1, 1))

    return dungeon


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    # max_monsters_per_room: int,
    # max_items_per_room: int,
    engine: Engine,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    # for row in range(len(dungeon.tiles)):
    #     for tile in range(len(row)):
    #         print(row, tile)

    # below here is tutorial stuff
    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # player.x, player.y = new_room.center
            player.place(*new_room.center, dungeon)
        else:
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

                center_of_last_room = new_room.center

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        rooms.append(new_room)

    return dungeon
