from __future__ import annotations
from typing import TYPE_CHECKING

from components.base_component import BaseComponent
# from resource_types import ResourceType

if TYPE_CHECKING:
  from entity import Resource, Item

class Harvestable(BaseComponent):
  parent: Resource

  def __init__(
      self,
      # resource_type: ResourceType,
      resource_item: Item,
      capacity: int = 100,
      #portion does nothing rn

      portion: int = 10,
  ):
    # self.resource_type = resource_type
    self.resource_item = resource_item
    self.capacity = capacity
    self.portion = portion

  def decrement(self) -> None:
    self.capacity -= self.portion
    if self.capacity <= 0:
      self.parent.gamemap.entities.remove(self.parent)

#this might be totally useless rn?
class Crystal(Harvestable):
  def __init__(self, resource_item, capacity = 100, portion = 10) -> None:
    super().__init__(resource_item=resource_item, capacity=capacity, portion=portion)