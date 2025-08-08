from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.fighter import Fighter


class Condition:
    parent: Fighter | None

    def __init__(
        self,
        name: str = "<Unnamed Condition>",
        duration: int | None = None,
    ):
        self.name = (name,)
        self.duration = duration
        self.parent = None

    def proc(self):
        if self.duration:
            self.duration -= 1
            if self.duration < 1:
                self.parent.conditions.remove(self)


class PoisonCondition(Condition):
    def __init__(
        self,
        name: str = "<Unnamed Poison>",
        duration: int | None = None,
        damage: int = 1,
    ):
        super().__init__(name=name, duration=duration)
        self.damage = damage

    def proc(self):
        self.parent.fighter.hp -= self.damage
        super().proc()
