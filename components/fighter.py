from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent

# from input_handlers import GameOverEventHandler
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor
    # from condition import Condition


class Fighter(BaseComponent):
    # entity: Actor
    parent: Actor

    def __init__(
        self,
        hp: int,
        base_armor: int = 0,
        base_dodge: int = 0,
        base_accuracy: int = 0,
        # attack_effect: Condition = None,
    ):
        self.max_hp = hp
        self._hp = hp
        self.base_armor = base_armor
        self.base_dodge = base_dodge
        self.base_accuracy = base_accuracy
        self.conditions = {}  # switched from list to dict for better condition lookup
        # self.attack_effect = attack_effect

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def armor(self) -> int:
        return self.base_armor + self.armor_bonus

    @property
    def dodge(self) -> int:
        return self.base_dodge + self.dodge_bonus

    @property
    def accuracy(self) -> int:
        return self.base_accuracy + self.accuracy_bonus

    @property
    def armor_bonus(self) -> int:
        if self.parent.equipment.armor:
            return self.parent.equipment.armor.equippable.armor_value
        else:
            return 0

    @property
    def dodge_bonus(self) -> int:
        if self.parent.equipment.armor:
            return self.parent.equipment.armor.equippable.dodge_value
        else:
            return 0

    @property
    def accuracy_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.accuracy_bonus
        else:
            return 0

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
            # self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        # print(death_message)
        self.engine.message_log.add_message(death_message, death_message_color)
        """
    disabled XP for now, currently it goes to the player no matter who kills it,
    which is no good. I also just don't know if i want XP in the game.
    """
        # self.engine.player.level.add_xp(self.parent.level.xp_given)
        self.engine.score += 100

        # drop items on death
        if self.parent.inventory:
            # for item in [
            #     item
            #     for item in self.parent.inventory.items
            #     if item.equippable.natural is False
            # ]:
            for item in self.parent.inventory.items:  # natural weapons maybe not needed
                item.place(self.parent.x, self.parent.y, self.gamemap)

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount
        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
