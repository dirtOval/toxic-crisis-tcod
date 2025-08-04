from __future__ import annotations
from typing import TYPE_CHECKING

from components.base_component import BaseComponent
# import entity_factories

if TYPE_CHECKING:
  from entity import MobSpawner, Actor

class Spawner(BaseComponent):
  parent: MobSpawner

  def __init__(
      self,
      mob: Actor,
      # delay: int = 1,
  ):
    self.mob = mob
    # self.delay = delay
    # self.timer = delay

  def spawn_mob(self) -> None:
    dungeon = self.parent.parent
    if not any(entity is not self.parent and entity.x == self.parent.x and entity.y == self.parent.y for entity in dungeon.entities):
      self.mob.spawn(dungeon, self.parent.x, self.parent.y)

class TimerSpawner(Spawner):
  def __init__(
    self,
    mob: Actor,
    delay: int = 1,
  ):
    super().__init__(
      mob=mob,
    )
    self.delay = self.timer = delay

  def decrement_timer(self) -> None:
    self.timer -= 1
    # print(f'{self.parent.name} timer: {self.timer}')
    if self.timer <= 0:
      self.spawn_mob()
      self.timer = self.delay

class EcoSpawner(Spawner):
  def __init__(
    self,
    mob: Actor,
    spawn_cost: int = 1,
    bank: int = 0,
  ):
    super().__init__(
      mob=mob,
    )
    self.spawn_cost = spawn_cost
    self.bank = bank

  def add_to_bank(self, amount: int):
    self.bank += amount

  def try_to_spawn(self) -> None:
    if self.bank >= self.spawn_cost:
      self.spawn_mob()
      self.bank -= self.spawn_cost
#superfluous, can set these in entity_factories and skip the import.

# class VirusTimerSpawner(TimerSpawner):
#   def __init__(self, delay = 5) -> None:
#     super().__init__(mob=entity_factories.virus, delay=delay)

# class GuardTimerSpawner(TimerSpawner):
#   def __init__(self, delay = 5) -> None:
#     super().__init__(mob=entity_factories.guard, delay=delay)