import tcod

# import copy
import traceback

import color

# from engine import Engine
# import entity_factories
import exceptions
import input_handlers

# from procgen import generate_dungeon
import setup_game
from actions import WaitAction
from time import sleep


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved!")


def main() -> None:
    terminal_width = 80
    terminal_height = 50
    auto_speed = 0.5

    tileset = tcod.tileset.load_tilesheet(
        "terminal10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new(
        # x=0,
        # y=0,
        # width=terminal_width,
        # height=terminal_height,
        columns=terminal_width,
        rows=terminal_height,
        tileset=tileset,
        title="Super Snake Hunter",
        vsync=True,
        sdl_window_flags=1,
    ) as context:
        root_console = tcod.console.Console(terminal_width, terminal_height, order="F")

        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)
                # if isinstance(handler, input_handlers.MainGameEventHandler) and handler.engine.auto_wait:
                #   handler = handler.handle_events(tcod.event.KeyDown(93, tcod.event.KeySym.KP_5, 0))
                #   sleep(auto_speed)
                #   queue = tcod.event.get()
                #   try:
                #     next
                #   # if next(queue):
                #   #   handler.engine.auto_wait = False

                #   #DOES NOT WORK RN.
                #   #i think i need to make an input handler to deal
                #   #with this. that can send actions to here.
                #   #less jank than doing it on main and also can
                #   #listen for ev_keydown to quit out
                # else:
                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc()
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # saving this time
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # save if something else breaks
            save_game(handler, "savegame.sav")
            raise


# boilerplate to make sure main only runs when the script is called
if __name__ == "__main__":
    main()

