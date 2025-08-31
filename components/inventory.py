from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int, items: List = []):
        self.capacity = capacity
        self.items: List[Item] = items

    def drop(self, item: Item) -> None:
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)
        self.engine.message_log.add_message(
            f"{self.parent.name} dropped the {item.name}."
        )

    def clear(self) -> None:
        self.items = []

    def instances_of(self, item_name):
        return filter(lambda item: item.name == item_name, self.items)

