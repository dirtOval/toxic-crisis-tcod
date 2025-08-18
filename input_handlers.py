from __future__ import annotations

import os
from math import ceil

from typing import Callable, Iterable, Optional, Tuple, TYPE_CHECKING, Union

import tcod.event

import actions
from actions import (
    Action,
    BumpAction,
    # EscapeAction,
    PickupAction,
    WaitAction,
)
from render_order import RenderOrder

import color
import exceptions
# for auto wait
# import time

# find out wtf TYPE_CHECKING is
if TYPE_CHECKING:
    from engine import Engine
    from entity import Item, Entity

MOVE_KEYS = {
    # arrow keys
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys. i don't like these lmao
    # tcod.event.KeySym.h: (-1, 0),
    # tcod.event.KeySym.j: (0, 1),
    # tcod.event.KeySym.k: (0, -1),
    # tcod.event.KeySym.l: (1, 0),
    # tcod.event.KeySym.y: (-1, -1),
    # tcod.event.KeySym.u: (1, -1),
    # tcod.event.KeySym.b: (-1, 1),
    # tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
    tcod.event.KeySym.SPACE,
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

# look up how Union works
ActionOrHandler = Union[Action, "BaseEventHandler"]


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    # essentially: if the event returns an event handler, return that
    # handler. otherwise, return the same event handler.
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()


class PopupMessage(BaseEventHandler):
    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        self.parent.on_render(console)
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

        def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
            return self.parent


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine
        # not working, must figure out
        # self.waiting = False

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        # NOT WORKING
        # if self.waiting:
        #   time.sleep(0.2)
        #   self.handle_action(WaitAction(self.engine.player))
        #   return MainGameEventHandler(self.engine)
        # else:
        #   action_or_state = self.dispatch(event)
        action_or_state = self.dispatch(event)

        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            if not self.engine.player.is_alive:
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)

            # if not dead or leveling up, handle conditions
            player_conditions = self.engine.player.fighter.conditions
            # print(f"player conditions: {player_conditions}")
            # for condition in player_conditions:
            #    print(
            #        f"duration of {player_conditions[condition].name}: {player_conditions[condition].duration}"
            #    )
            condition_removal = []
            for condition in player_conditions:  # this should only affect players?
                if player_conditions[condition] is not None:
                    player_conditions[condition].proc()
                else:
                    condition_removal.append(condition)
            for condition in condition_removal:
                player_conditions.pop(condition)

            return MainGameEventHandler(self.engine)
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True

    # def handle_events(self, context: tcod.context.Context) -> None:
    #   for event in tcod.event.wait():
    #     context.convert_event(event)
    #     self.dispatch(event)

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        int_x, int_y = int(event.tile.x), int(event.tile.y)
        if self.engine.game_map.in_bounds(int_x, int_y):
            self.engine.mouse_location = int_x, int_y

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class AskUserEventHandler(EventHandler):
    # def handle_action(self, action: Optional[Action]) -> bool:
    #   if super().handle_action(action):
    #     self.engine.event_handler = MainGameEventHandler(self.engine)
    #     return True
    #   return False
    # subclass event handler that will return to main game handler when selection is made/action is performed

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        if event.sym in {
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:  # these are the only keys that will not result in exit
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        # self.engine.event_handler = MainGameEventHandler(self.engine)
        return MainGameEventHandler(self.engine)


# probably wanna disable this later
class DebugMenuEventHandler(AskUserEventHandler):
    TITLE = "Debug"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        width = 40

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=7,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=y + 1, string=f"1) do FOV? [{self.engine.do_fov}]")
        console.print(
            x=x + 1,
            y=y + 2,
            string=f"2) player is ghost? [{self.engine.player_is_ghost}]",
        )
        console.print(
            x=x + 1,
            y=y + 3,
            string=f"3) player teleport? (num +) [{self.engine.player_teleport}]",
        )
        """
    TO DO!
    -ghost player -- done!
    -freeze events
    -teleport -- done!
    -spawner
    -auto-wait -- this needs a lot more thought
    """

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        if event.sym == tcod.event.KeySym.N1:
            self.engine.do_fov = not self.engine.do_fov
            self.engine.update_fov()
            print(f"do_fov: {self.engine.do_fov}")
        elif event.sym == tcod.event.KeySym.N2:
            self.engine.player_is_ghost = not self.engine.player_is_ghost
            print(f"player_is_ghost: {self.engine.player_is_ghost}")
            self.engine.player.blocks_movement = (
                False if self.engine.player_is_ghost else True
            )
            self.engine.player.render_order = (
                RenderOrder.GHOST if self.engine.player_is_ghost else RenderOrder.ACTOR
            )
        elif event.sym == tcod.event.KeySym.N3:
            self.engine.player_teleport = not self.engine.player_teleport
            print(f"player_teleport: {self.engine.player_teleport}")
        else:
            return super().ev_keydown(event)


class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=7,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}"
        )
        console.print(
            x=x + 1,
            y=y + 3,
            string=f"XP for next Level: {self.engine.player.level.experience_to_next_level}",
        )
        console.print(
            x=x + 1, y=y + 4, string=f"Power: {self.engine.player.fighter.power}"
        )
        console.print(
            x=x + 1, y=y + 5, string=f"Defense: {self.engine.player.fighter.defense}"
        )


class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=1, string="Congrats! You level up!")
        console.print(x=x + 1, y=2, string="Select an attribute to increase.")

        console.print(
            x=x + 1,
            y=4,
            string=f"a) HP (+20, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x=x + 1,
            y=5,
            string=f"b) Power (+1, from {self.engine.player.fighter.power})",
        )
        console.print(
            x=x + 1,
            y=6,
            string=f"c) Defense (+1, from {self.engine.player.fighter.defense})",
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.A
        # print(f'key = {key}, tcod.event.KeySym.A = {tcod.event.KeySym.A}, index = {index}')
        # ^ so i can understand how tf this works
        # a's code is 97, b is 98, c is 99. that's how it works.

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_power()
            else:
                player.level.increase_defense()
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)

            return None

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        return None  # no clicking out of level up menu


class InventoryEventHandler(AskUserEventHandler):
    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                # console.print(x + 1, y + i + 1, f'({item_key}) {item.name}')

                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key}) {item.get_name()}"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                console.print(x + 1, y + i + 1, item_string)
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.A

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player, item)
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        return actions.DropItem(self.engine.player, item)


class SpawnerMenuHandler(AskUserEventHandler):
    # the solution right now is to paginate. first 26 items get grouped,
    # then when player hits arrow key the next group of 26 gets grouped.
    # if less than 26, it'll cycle back to top.
    # can add a page variable, will use that to offset selection in pages after the first

    # update: im dumb. just need to return another spawnermenu handler with the page initiated as the subsequent one.
    # so i need to pass in the page, with 1 as default.

    # not workign right now. pagination should be working but the console needs to rerender.
    # probably need to make a sub console like in history viewer, just need to figure out how to do that.
    def __init__(self, engine: Engine, page: int = 1):
        super().__init__(engine)
        self.TITLE = "Spawner Menu"
        self.multispawn = False
        self.number_of_entities = len(self.engine.entity_dict)
        self.page = page

    # it seems inefficient to calculate this on the fly, but it bugs when i try to store it?
    # maybe can just store the enumerable on engine? mess with this later.
    @property
    def entity_list(self) -> Iterable:
        # return enumerate(self.engine.entity_list)
        return list(self.engine.entity_dict.items())

    @property
    def current_page_contents(self) -> Iterable:
        start = 0 + (26 * (self.page - 1))
        end = 26 * self.page
        if end > self.number_of_entities:
            end = self.number_of_entities
        return self.entity_list[start:end]

    @property
    def page_count(self) -> int:
        return ceil(self.number_of_entities / 26)

    # def render_contents(self, console: tcod.Console):
    #   height = self.number_of_entities + 2

    #   if height <= 3:
    #     height = 3

    #   if self.engine.player.x <= 30:
    #     x = 40
    #   else:
    #     x = 0

    #   y = 0

    #   width = len(self.TITLE) + 20

    #   console.draw_frame(
    #     x=x,
    #     y=y,
    #     width=width,
    #     height=height,
    #     title=self.TITLE,
    #     clear=True,
    #     fg=(255, 255, 255),
    #     bg=(0, 0, 0),
    #   )

    #   console.print(x + 1, y + 1, f'TAB) multi-spawn? [{self.multispawn}]')

    #   if self.number_of_entities > 0:
    #     # for i, entity in self.entity_enumerable:
    #     for i, entity in enumerate(self.current_page_contents):
    #       entity_key = chr(ord('a') + i)

    #       entity_string = f'({entity_key}) {entity.name}'

    #       console.print(x + 1, y + i + 2, entity_string)
    #       # console.print(x + 1, y + i + 2, entity)
    #   else:
    #     console.print(x + 1, y + 1, '(Empty)')

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        # self.render_contents(console)
        # print(self.number_of_entities)

        height = self.number_of_entities + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 20

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x + 1, y + 1, f"TAB) multi-spawn? [{self.multispawn}]")

        if self.number_of_entities > 0:
            # for i, entity in self.entity_enumerable:
            for i, entity in enumerate(self.current_page_contents):
                entity_key = chr(ord("a") + i)

                entity_string = f"({entity_key}) {entity[1].name}"

                console.print(x + 1, y + i + 2, entity_string)
                # console.print(x + 1, y + i + 2, entity)
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        # player = self.engine.player
        key = event.sym
        if key == tcod.event.KeySym.TAB:
            self.multispawn = not self.multispawn
            return None
        elif key == tcod.event.KeySym.RIGHT:
            self.page += 1
            # print(f'page: {self.page}')
            if self.page > self.page_count:
                # print('rolling back to 1')
                # self.page = 1
                return SpawnerMenuHandler(self.engine, 1)
            else:
                return SpawnerMenuHandler(self.engine, self.page)
            # self.render_contents()
            # return None
        elif key == tcod.event.KeySym.LEFT:
            self.page -= 1
            if self.page < 1:
                return SpawnerMenuHandler(self.engine, self.page_count)
            else:
                return SpawnerMenuHandler(self.engine, self.page)
        else:
            index = key - tcod.event.KeySym.A
            if 0 <= index <= 26:
                try:
                    # selected_item = player.inventory.items[index]
                    # print(list(self.entity_enumerable))
                    entity_to_spawn = self.engine.entity_dict[
                        self.entity_list[index + (self.page - 1) * 26][0]
                    ]
                    # ^need to make this respect pagination!!
                except IndexError:
                    self.engine.message_log.add_message("Invalid entry.", color.invalid)
                    return None
                # return self.on_item_selected(selected_item)
                return SpawnPlacementHandler(
                    self.engine, entity_to_spawn, self.multispawn
                )
        return super().ev_keydown(event)


class SelectIndexHandler(AskUserEventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # holding modifier keys will speed up movement
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier

            # prevent out of bounds
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        int_x, int_y = int(event.tile.x), int(event.tile.y)
        if self.engine.game_map.in_bounds(int_x, int_y):
            if event.button == 1:
                return self.on_index_selected(int_x, int_y)
            return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    # for looking around a la every roguelike
    def on_index_selected(self, x: int, y: int) -> None:
        # self.engine.event_handler = MainGameEventHandler(self.engine)
        return MainGameEventHandler(self.engine)


class PlayerTeleportHandler(SelectIndexHandler):
    # debug tool to teleport player around map
    def on_index_selected(self, x: int, y: int) -> None:
        self.engine.player.x = x
        self.engine.player.y = y
        return MainGameEventHandler(self.engine)


class SpawnPlacementHandler(SelectIndexHandler):
    def __init__(self, engine: Engine, entity: Entity, multispawn: bool):
        super().__init__(engine)
        self.entity = entity
        self.multispawn = multispawn

    def on_index_selected(self, x: int, y: int) -> None:
        self.entity.spawn(self.engine.game_map, x, y)
        if self.multispawn == False:
            return MainGameEventHandler(self.engine)
        else:
            return None


class SingleRangedAttackHandler(SelectIndexHandler):
    def __init__(
        self,
        engine: Engine,
        callback: Callable[[Tuple[int, int]], Optional[ActionOrHandler]],
    ):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[ActionOrHandler]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        x, y = self.engine.mouse_location

        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius**2,
            height=self.radius**2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        return self.callback((x, y))


class MainGameEventHandler(EventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player

        if key == tcod.event.KeySym.PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.KeySym.ESCAPE:
            # action = EscapeAction(player)
            raise SystemExit()

        elif key == tcod.event.KeySym.V:
            return HistoryViewer(self.engine)

        elif key == tcod.event.KeySym.G:
            action = PickupAction(player)

        elif key == tcod.event.KeySym.I:
            return InventoryActivateHandler(self.engine)

        elif key == tcod.event.KeySym.D:
            return InventoryDropHandler(self.engine)

        elif key == tcod.event.KeySym.L:
            return LookHandler(self.engine)

        elif key == tcod.event.KeySym.F:
            return SingleRangedAttackHandler(
                self.engine,
                callback=lambda xy: actions.RangedAction(self.engine.player, xy),
            )

        elif key == tcod.event.KeySym.C:
            return CharacterScreenEventHandler(self.engine)

        # debugger activate
        elif key == tcod.event.KeySym.GRAVE:
            # self.engine.debug_mode = not self.engine.debug_mode
            # print(f'debug mode = {self.engine.debug_mode}')
            return DebugMenuEventHandler(self.engine)

        # debug tools
        elif key == tcod.event.KeySym.KP_MULTIPLY:
            if self.engine.player_teleport:
                return PlayerTeleportHandler(self.engine)

        elif key == tcod.event.KeySym.KP_PLUS:
            return SpawnerMenuHandler(self.engine)

        elif key == tcod.event.KeySym.KP_PERIOD:
            self.engine.auto_wait = not self.engine.auto_wait

        # auto-wait enable -- NOT WORKING
        # elif key == tcod.event.KeySym.KP_PERIOD:
        #   self.waiting = not self.waiting
        # return AutoWaitEventHandler(self.engine)

        return action


# class AutoWaitEventHandler(EventHandler):
#   # def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
#     # key = event.sym
#     # if key
#   def __init__(self, engine: Engine):
#     self.engine = engine
#     self.waiting = True

#   def handle_events(self, key: tcod.event.KeySym) -> BaseEventHandler:
#     while self.waiting:
#       time.sleep(0.5)
#       self.engine.handle_enemy_turns()
#       # self.on_render()
#       return AutoWaitEventHandler(self.engine)
#     # return MainGameEventHandler(self.engine)


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")
        raise exceptions.QuitWithoutSaving()

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            raise SystemExit()


class HistoryViewer(EventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # keeps drawing main state behind

        log_console = tcod.Console(console.width - 6, console.height - 6)

        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "~|Message History|~", alignment=tcod.CENTER
        )

        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1
        else:
            return MainGameEventHandler(self.engine)
        return None
