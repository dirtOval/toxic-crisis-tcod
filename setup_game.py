from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod

import color
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers
from procgen import generate_dungeon
from render_order import RenderOrder

background_image = tcod.image.load("menu_background.png")[:, :, :3]


def test_level() -> Engine:
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
    )
    engine.game_world.generate_test_level()
    engine.do_fov = False

    engine.player_is_ghost = True
    player.blocks_movement = False
    player.render_order = RenderOrder.GHOST

    engine.player_teleport = True
    engine.update_fov()

    engine.message_log.add_message("TEST LEVEL", color.welcome_text)

    rifle = copy.deepcopy(entity_factories.ar_150)
    knife = copy.deepcopy(entity_factories.combat_knife)
    armor = copy.deepcopy(entity_factories.ballistic_vest)

    rifle.parent = player.inventory
    knife.parent = player.inventory
    armor.parent = player.inventory

    player.inventory.items.append(rifle)
    player.equipment.toggle_equip(rifle, add_message=False)
    player.inventory.items.append(knife)
    player.equipment.toggle_equip(knife, add_message=False)
    player.inventory.items.append(armor)
    player.equipment.toggle_equip(armor, add_message=False)

    return engine


def new_game() -> Engine:
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    # max_monsters_per_room = 2
    # max_items_per_room = 2

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        # max_monsters_per_room=max_monsters_per_room,
        # max_items_per_room=max_items_per_room,
    )
    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message("NEW GAME", color.welcome_text)

    rifle = copy.deepcopy(entity_factories.rifle)
    ballistic_vest = copy.deepcopy(entity_factories.ballistic_vest)

    rifle.parent = player.inventory
    ballistic_vest.parent = player.inventory

    player.inventory.items.append(rifle)
    player.equipment.toggle_equip(rifle, add_message=False)
    player.inventory.items.append(ballistic_vest)
    player.equipment.toggle_equip(ballistic_vest, add_message=False)

    return engine


def load_game(filename: str) -> Engine:
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)

    return engine


class MainMenu(input_handlers.BaseEventHandler):
    def on_render(self, console: tcod.console.Console) -> None:
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "ROGUELIKE TEST GAME",
            fg=color.menu_title,
            alignment=tcod.libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "FORTRESS ACCIDENT",
            fg=color.menu_title,
            alignment=tcod.libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            [
                "[N] Play Tutorial Game",
                "[C] Continue last game",
                "[T] Test Level",
                "[Q] Quit",
            ]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.libtcodpy.CENTER,
                bg_blend=tcod.libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.Q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.C:
            # pass #load game
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.N:
            return input_handlers.MainGameEventHandler(new_game())
        elif event.sym == tcod.event.KeySym.T:
            return input_handlers.MainGameEventHandler(test_level())

        return None
