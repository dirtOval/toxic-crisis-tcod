# from typing import Set, Iterable, Any

from __future__ import annotations

import lzma
import pickle

from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov
# from tcod import FOV_SYMMETRIC_SHADOWCAST

import exceptions

# from input_handlers import MainGameEventHandler
from message_log import MessageLog
import render_functions
import entity_factories
from entity import Entity

if TYPE_CHECKING:
    # from entity import Entity
    from entity import Actor
    from game_map import GameMap, GameWorld
    # from input_handlers import EventHandler


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location: tuple[int, int] = (0, 0)
        self.player = player
        # should write a script to import this on setup and turn it into a useful shape
        self.entity_dict = dict(
            [
                (var, obj)
                for var, obj in entity_factories.__dict__.items()
                if isinstance(obj, Entity)
            ]
        )
        # self.debug_mode = False
        # debug switches
        self.do_fov = True
        self.player_is_ghost = False
        self.player_teleport = False
        self.auto_wait = False
        self.score = 0
        self.police_called = False

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            # print(f'The {entity.name} does nothing on its turn :P')
            if entity.ai:
                condition_removal = []
                for condition in entity.fighter.conditions:
                    if entity.fighter.conditions[condition] is not None:
                        entity.fighter.conditions[
                            condition
                        ].proc()  # if poisoned, take damage for instance
                    else:
                        condition_removal.append(condition)
                for condition in condition_removal:
                    entity.fighter.conditions.pop(condition)
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # plays dont need to know every time AI fails attempt

    def update_fov(self) -> None:
        fov_radius = 8 if self.do_fov else 0
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=fov_radius,  # should make this a variable later. flashlight/torch etc
            # fuck with FOV algorithm
        )
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=51, y=9, width=28, height=40)

        console.print(x=51, y=2, string="Big Snake Hunter")

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        console.print(x=51, y=5, string=f"Score: {self.score}")

        # render_functions.render_dungeon_level(
        #    console=console,
        #    dungeon_level=self.game_world.current_floor,
        #    location=(0, 47),
        # )

        render_functions.render_names_at_mouse_location(
            console=console, x=51, y=8, engine=self
        )

    def save_as(self, filename: str) -> None:
        # data = {
        #     "game_map": self.game_map,
        #     "game_world": self.game_world,
        #     "message_log": self.message_log,
        #     "player": self.player,
        #     "entity_dict": self.entity_dict,
        #     "do_fov": self.do_fov,
        #     "player_is_ghost": self.player_is_ghost,
        #     "player_teleport": self.player_teleport,
        #     "auto_wait": self.auto_wait,
        # }
        # save_data = lzma.compress(pickle.dumps(self))
        # save_data = lzma.compress(pickle.dumps(data))
        # with open(filename, "wb") as f:
        #     f.write(save_data)
        print("need to add saving back in with dill maybe? lmao oops SDL3")
