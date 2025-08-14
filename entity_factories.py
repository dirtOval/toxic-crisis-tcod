import components.ai as ai

# from components import consumable, equippable
from components.equippable import Weapon, RangedWeapon, Armor
from components.harvestable import Harvestable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.spawner import TimerSpawner, EcoSpawner
from entity import Actor, Item, MobSpawner, Resource
from color import guard_pink, virus_teal, snake_green
from condition import PoisonCondition

# player = Entity(char='@', color=(255, 255, 255), name='Player', blocks_movement=True)
player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=ai.Combatant,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
    faction="player",
)

# CONDITIONS
mamba_madness = PoisonCondition(
    name="Mamba Madness",
    duration=3,
    damage=3,
)

# toxic crisis mobs
snake = Actor(
    char="s",
    color=snake_green,
    name="Green Mamba",
    ai_cls=ai.Combatant,
    equipment=Equipment(),
    fighter=Fighter(hp=6, base_defense=0, base_power=5, attack_effect=mamba_madness),
    inventory=Inventory(capacity=1),
    level=Level(xp_given=1),
    faction="snake",
)

# PC weapons
ar_150 = Item(
    char=")",
    color=(15, 15, 15),
    name="AR-150",
    equippable=RangedWeapon(
        accuracy=2,
        armor_penetration=1,
        damage=6,
        range=15,
        ammo_type=None,  # add 5.56mm later
    ),
)
# PC armor
ballistic_vest = Item(
    char="]",
    color=(15, 50, 15),
    name="Ballistic Vest",
    equippable=Armor(
        armor_value=2,
        dodge_value=0,
    ),
)

# mob weapons

# mob armor

###########################################################
# OLD SHIT
# allied mobs
# guard = Actor(
#    char="g",
#    color=guard_pink,
#    name="Guard",
#    ai_cls=ai.Combatant,
#    equipment=Equipment(),
#    fighter=Fighter(hp=10, base_defense=0, base_power=4),
#    inventory=Inventory(capacity=1),
#    level=Level(xp_given=0),
#    faction="player",
# )
#
# guard_miner = Actor(
#    char="m",
#    color=guard_pink,
#    name="Guard Miner",
#    ai_cls=ai.MinerAI,
#    equipment=Equipment(),
#    fighter=Fighter(hp=5, base_defense=0, base_power=1),
#    inventory=Inventory(capacity=1),
#    level=Level(xp_given=0),
#    faction="player",
# )
#
## hostile mobs
# virus = Actor(
#    char="v",
#    color=virus_teal,
#    name="Virus",
#    ai_cls=ai.Combatant,
#    equipment=Equipment(),
#    fighter=Fighter(hp=10, base_defense=0, base_power=4),
#    inventory=Inventory(capacity=0),
#    level=Level(xp_given=35),
#    faction="hostile",
# )
#
# virus_miner = Actor(
#    char="m",
#    color=virus_teal,
#    name="Virus Miner",
#    ai_cls=ai.MinerAI,
#    equipment=Equipment(),
#    fighter=Fighter(hp=5, base_defense=0, base_power=1),
#    inventory=Inventory(capacity=1),
#    level=Level(xp_given=0),
#    faction="hostile",
# )
#
#
## mob spawners
# virus_eco_spawner = MobSpawner(
#    char="O",
#    color=virus_teal,
#    name="Virus EcoSpawner",
#    fighter=Fighter(hp=20, base_defense=3, base_power=0),
#    level=Level(xp_given=50),
#    ai_cls=ai.EcoSpawnerAI,
#    spawner=EcoSpawner(virus, 1, 0),
#    faction="hostile",
# )
#
# virus_timer_spawner = MobSpawner(
#    char="O",
#    color=virus_teal,
#    name="Virus TimerSpawner",
#    fighter=Fighter(hp=20, base_defense=3, base_power=0),
#    level=Level(xp_given=50),
#    ai_cls=ai.TimerSpawnerAI,
#    spawner=TimerSpawner(virus, 5),
#    faction="hostile",
# )
#
# guard_eco_spawner = MobSpawner(
#    char="O",
#    color=guard_pink,
#    name="Guard EcoSpawner",
#    fighter=Fighter(hp=20, base_defense=3, base_power=0),
#    level=Level(xp_given=50),
#    ai_cls=ai.EcoSpawnerAI,
#    spawner=EcoSpawner(guard, 1, 0),
#    faction="player",
# )
#
# guard_timer_spawner = MobSpawner(
#    char="O",
#    color=guard_pink,
#    name="Guard TimerSpawner",
#    fighter=Fighter(hp=20, base_defense=3, base_power=0),
#    level=Level(xp_given=50),
#    ai_cls=ai.TimerSpawnerAI,
#    spawner=TimerSpawner(guard, 5),
#    faction="player",
# )
#
## resource items
# crystal = Item(
#    char="c",
#    color=(7, 227, 247),
#    name="Crystal",
#    max_stack=3,
# )
#
## resource wells
# crystal_well = Resource(
#    char="C",
#    color=(7, 227, 247),
#    name="Crystal Well",
#    harvestable=Harvestable(
#        resource_item=crystal,
#        capacity=10,
#        portion=1,
#    ),
# )
#
#
## TUTORIAL STUFF-------------------------------------------
# orc = Actor(
#    char="o",
#    color=(63, 127, 63),
#    name="Orc",
#    ai_cls=ai.Combatant,
#    equipment=Equipment(),
#    fighter=Fighter(hp=10, base_defense=0, base_power=4),
#    inventory=Inventory(capacity=0),
#    level=Level(xp_given=35),
#    faction="hostile",
# )
# troll = Actor(
#    char="T",
#    color=(0, 127, 0),
#    name="Troll",
#    ai_cls=ai.Combatant,
#    equipment=Equipment(),
#    fighter=Fighter(hp=16, base_defense=1, base_power=8),
#    inventory=Inventory(capacity=0),
#    level=Level(xp_given=100),
#    faction="hostile",
# )
#
## #ITEMS -- TUTORIAL
# confusion_scroll = Item(
#    char="~",
#    color=(207, 63, 255),
#    name="Confusion Scroll",
#    consumable=consumable.ConfusionConsumable(number_of_turns=10),
# )
# fireball_scroll = Item(
#    char="~",
#    color=(255, 0, 0),
#    name="Fireball Scroll",
#    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
# )
# health_potion = Item(
#    char="!",
#    color=(127, 0, 255),
#    name="Health Potion",
#    consumable=consumable.HealingConsumable(amount=4),
# )
# lightning_scroll = Item(
#    char="~",
#    color=(255, 255, 0),
#    name="Lightning Scroll",
#    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
# )
#
## ranged weapons
# bow = Item(char=")", color=(255, 0, 0), name="Bow", equippable=equippable.Bow())
#
## ammo
# quiver = Item(
#    char="^",
#    color=(155, 155, 155),
#    name="Quiver of Arrows",
#    consumable=consumable.Consumable(),
#    amount=10,
#    max_stack=10,
# )
#
## equipment -- tutorial
#
# dagger = Item(
#    char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
# )
#
# sword = Item(char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword())
#
# leather_armor = Item(
#    char="[",
#    color=(139, 69, 19),
#    name="Leather Armor",
#    equippable=equippable.LeatherArmor(),
# )
#
# chain_mail = Item(
#    char="[",
#    color=(139, 69, 19),
#    name="Chain Mail",
#    equippable=equippable.ChainMail(),
# )
