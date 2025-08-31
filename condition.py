from typing import TYPE_CHECKING
from random import randint

if TYPE_CHECKING:
    from components.fighter import Fighter


class Condition:
    parent: None

    def __init__(
        self,
        name: str = "<Unnamed Condition>",
        afflict_message: str = " gets sick with <Unnamed Condition>",
        cure_message: str = " is no longer sick with <Unnamed Condition",
        duration: int | None = None,
    ):
        self.name = name
        self.afflict_message = afflict_message
        self.cure_message = cure_message
        self._initial_duration = duration
        self.duration = duration
        self.parent = None

    def proc(self):
        if self.duration:
            self.duration -= 1
            if self.duration < 1:
                self.parent.parent.engine.message_log.add_message(
                    self.parent.name + self.cure_message
                )
                self.parent.fighter.conditions[self.name] = None

    def extend_condition(self):
        self.duration += randint(1, self._initial_duration)


class PoisonCondition(Condition):
    def __init__(
        self,
        name: str = "<Unnamed Poison>",
        afflict_message: str = " gets sick with <Unnamed Poison>",
        cure_message: str = " is no longer sick with <Unnamed Poison>",
        duration: int | None = None,
        damage_die: int = 1,
    ):
        super().__init__(
            name=name,
            afflict_message=afflict_message,
            cure_message=cure_message,
            duration=duration,
        )
        self.damage_die = damage_die
        self.damage = randint(1, damage_die)

    def proc(self):
        self.parent.fighter.hp -= self.damage
        self.parent.parent.engine.message_log.add_message(
            f"{self.parent.name} takes {self.damage} damage from poison.", (255, 0, 0)
        )
        super().proc()

    def extend_condition(self):
        super().extend_condition()
        self.damage += randint(1, self.damage_die)
        self.parent.parent.engine.message_log.add_message(
            f"{self.parent.name}'s {self.name} gets worse!"
        )
