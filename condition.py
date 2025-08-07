from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.fighter import Fighter


class Condition:
    parent: Fighter

    def __init__(
        self,
        parent: Fighter | None,
        name: str = "<Unnamed Condition>",
        duration: int | None = None,
    ):
        self.name = (name,)
        self.duration = duration

    def proc(self):
        if duration:
            duration -= 1
            if duration < 1:
                parent.conditions.remove(self)
