from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, DepositAction, MeleeAction, MineAction, MovementAction, WaitAction, BumpAction
# from components.base_component import BaseComponent

from entity import MobSpawner
if TYPE_CHECKING:
  from entity import Actor, Resource

# class BaseAI(Action, BaseComponent):
class BaseAI(Action):
  # entity: Actor

  def perform(self) -> None:
    raise NotImplementedError()
  
  #is this useful? idk
  def get_distance(self, x: int, y: int):
    dx = x - self.entity.x
    dy = y - self.entity.y
    return max(abs(dx), abs(dy))
  
  def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
    #list bc it returns a coordinate path
    cost = np.array(self.entity.gamemap.tiles['walkable'], dtype=np.int8)

    for entity in self.entity.gamemap.entities:
      if entity.blocks_movement and cost[entity.x, entity.y]:
        cost[entity.x, entity.y] += 10

    graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
    pathfinder = tcod.path.Pathfinder(graph)

    pathfinder.add_root((self.entity.x, self.entity.y))

    path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

    return [(index[0], index[1]) for index in path]
  
  # def get_closest_hostile(self, faction: str =''):
  
class ConfusedEnemy(BaseAI): #move randomly, attacking any actor it runs into
  def __init__(
      self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
  ):
    super().__init__(entity)

    self.previous_ai = previous_ai
    self.turns_remaining = turns_remaining

  def perform(self) -> None:
    if self.turns_remaining <= 0:
      self.engine.message_log.add_message(
        f'The {self.entity.name} is no longer confused.'
      )
      self.entity.ai = self.previous_ai
    else:
      direction_x, direction_y = random.choice(
        [
          (-1, -1),
          (0, 1),
          (1, -1),
          (-1, 0),
          (1, 0),
          (-1, 1),
          (0, 1),
          (1, 1),
        ]
      )

      self.turns_remaining -= 1

      return BumpAction(self.entity, direction_x, direction_y).perform()


class Combatant(BaseAI):

  '''
  ideally the hostile AI should:
  1. identify which enemy is closest and path to them
  2. break off pursuit and find a new enemy if far enough away
  
  '''

  def __init__(self, entity: Actor):
    super().__init__(entity)
    self.path: List[Tuple[int, int]] = []

  def get_closest_enemy(self) -> Actor:
    return self.entity.get_closest_entity(
      [actor for actor in self.entity.gamemap.actors
        if actor.faction != self.entity.faction]
    )

  def perform(self) -> None:
    # target = self.engine.player
    target = self.get_closest_enemy()
    
    if target:

      dx = target.x - self.entity.x
      dy = target.y - self.entity.y
      #look up Chebyshev distance
      distance = max(abs(dx), abs(dy))

      if self.engine.game_map.visible[self.entity.x, self.entity.y]:
        if distance <= 1:
          return MeleeAction(self.entity, dx, dy).perform()
        
        self.path = self.get_path_to(target.x, target.y)

      if self.path:
        dest_x, dest_y = self.path.pop(0)
        return MovementAction(
          self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
        ).perform()
    
    return WaitAction(self.entity).perform()
  
class MinerAI(BaseAI):

  def __init__(self, entity: Actor):
    super().__init__(entity)
    self.path: List[Tuple[int, int]] = []

  def get_closest_resource(self) -> Resource:
    return self.entity.get_closest_entity(
      [entity for entity in self.entity.gamemap.resources]
    )
  
  def get_closest_friendly_spawner(self) -> MobSpawner:
    return self.entity.get_closest_entity(
      [entity for entity in self.entity.gamemap.actors if isinstance(entity, MobSpawner) and entity.faction == self.entity.faction]
    )
  
  #pathing to target and executing action if in range and movement otherwise could be its own function.
  def seek_resource(self) -> None:
    target = self.get_closest_resource()
    if target:
      dx = target.x - self.entity.x
      dy = target.y - self.entity.y
      distance = max(abs(dx), abs(dy))

      if self.engine.game_map.visible[self.entity.x, self.entity.y]:
        if distance <= 1:
          return MineAction(self.entity, dx, dy).perform()
        
        self.path = self.get_path_to(target.x, target.y)

      if self.path:
        dest_x, dest_y = self.path.pop(0)
        return MovementAction(
          self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
        ).perform()
    
  def seek_spawner(self) -> None:
    target = self.get_closest_friendly_spawner()
    if target:
      dx = target.x - self.entity.x
      dy = target.y - self.entity.y
      distance = max(abs(dx), abs(dy))

      if self.engine.game_map.visible[self.entity.x, self.entity.y]:
        if distance <= 1:
          return DepositAction(self.entity, dx, dy).perform()
        
        self.path = self.get_path_to(target.x, target.y)

      if self.path:
        dest_x, dest_y = self.path.pop(0)
        return MovementAction(
          self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
        ).perform()
  
  def perform(self) -> None:

    can_harvest = len(self.entity.inventory.items) < self.entity.inventory.capacity

    if can_harvest:
      self.seek_resource()
      # dx = target.x - self.entity.x
      # dy = target.y - self.entity.y
      # distance = max(abs(dx), abs(dy))

      # if self.engine.game_map.visible[self.entity.x, self.entity.y]:
      #   if distance <= 1:
      #     return MineAction(self.entity, dx, dy).perform()
        
      #   self.path = self.get_path_to(target.x, target.y)

      # if self.path:
      #   dest_x, dest_y = self.path.pop(0)
      #   return MovementAction(
      #     self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
      #   ).perform()
    else:
      self.seek_spawner()
    
    return WaitAction(self.entity).perform()
    

#these two could probably be the same,
#overload their spawn mechanism with same name. derp.
class EcoSpawnerAI(BaseAI):
  def perform(self) -> None:
    self.entity.spawner.try_to_spawn()
    return WaitAction(self.entity).perform()

class TimerSpawnerAI(BaseAI):
  def __init__(self, entity: MobSpawner):
    super().__init__(entity)

  def perform(self) -> None:
    self.entity.spawner.decrement_timer()
    return WaitAction(self.entity).perform()