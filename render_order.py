from enum import auto, Enum

class RenderOrder(Enum):
  CORPSE = auto()
  ITEM = auto()
  STRUCTURE = auto()
  ACTOR = auto()
  GHOST = auto()