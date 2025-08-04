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
        self.mouse_location = (0, 0)
        self.player = player
        #should write a script to import this on setup and turn it into a useful shape
        self.entity_dict = dict([(var, obj) for var, obj in entity_factories.__dict__.items() if isinstance(obj, Entity)])
        # self.debug_mode = False
        #debug switches
        self.do_fov = True
        self.player_is_ghost = False
        self.player_teleport = False
        self.auto_wait = False

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            # print(f'The {entity.name} does nothing on its turn :P')
            if entity.ai:
                try:
                  entity.ai.perform()
                except exceptions.Impossible:
                    pass #plays dont need to know every time AI fails attempt

    def update_fov(self) -> None:
        fov_radius = 8 if self.do_fov else 0
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles['transparent'],
            (self.player.x, self.player.y),
            radius=fov_radius, #should make this a variable later. flashlight/torch etc
            #fuck with FOV algorithm
        )
        self.game_map.explored |= self.game_map.visible
            
    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)
        
        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        render_functions.render_names_at_mouse_location(
            console=console, x=21, y=44, engine=self
        )
    
    def save_as(self, filename: str) -> None:
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, 'wb') as f:
            f.write(save_data)