from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Item
    from condition import Condition

# from entity_factories import Arrow


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        # natural: bool = False,
        #  power_bonus: int = 0,
        #  defense_bonus: int = 0,
    ):
        self.equipment_type = equipment_type

        # self.power_bonus = power_bonus
        # self.defense_bonus = defense_bonus


class Armor(Equippable):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType = EquipmentType.ARMOR,
        # natural: bool = False,
        armor_value: int = 0,
        dodge_value: int = 0,
    ):
        super().__init__(
            equipment_type=equipment_type,
            # natural=natural,
        )
        self.armor_value = armor_value
        self.dodge_value = dodge_value


class Weapon(Equippable):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType = EquipmentType.WEAPON,
        #    power_bonus: int = 0,
        #    defense_bonus: int = 0,
        # natural: bool = False,
        accuracy: int = 0,
        armor_penetration: int = 0,
        damage: int = 1,
        effect: Condition = None,
    ):
        super().__init__(
            equipment_type=equipment_type,
            # natural=natural,
            # power_bonus=power_bonus,
            # defense_bonus=defense_bonus
        )
        # doesnt do anything rn, should mitigate or negate damage
        self.accuracy = accuracy
        self.armor_penetration = armor_penetration
        self.damage = damage
        self.effect = effect


class RangedWeapon(Weapon):
    parent: Item

    def __init__(
        self,
        #  power_bonus: int = 0,
        #  defense_bonus: int = 0,
        # natural: bool = False,
        accuracy: int = 0,
        armor_penetration: int = 0,
        damage: int = 1,
        range: int = 0,
        ammo_type: Item = None,
    ):
        super().__init__(
            equipment_type=EquipmentType.RANGED,
            #  power_bonus=power_bonus,
            #  defense_bonus=defense_bonus,
            # natural=natural,
            accuracy=accuracy,
            armor_penetration=armor_penetration,
            damage=damage,
        )
        self.range = range
        self.ammo_type = ammo_type


# class Dagger(Weapon):
#    def __init__(self) -> None:
#        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=2)
#
#
# class Sword(Weapon):
#    def __init__(self) -> None:
#        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=4)
#
#
# class LeatherArmor(Equippable):
#    def __init__(self) -> None:
#        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=1)
#
#
# class ChainMail(Equippable):
#    def __init__(self) -> None:
#        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=3)
#
#
# class Bow(RangedWeapon):
#    def __init__(self) -> None:
#        # add ammo later!
#        super().__init__(defense_bonus=0, power_bonus=10, range=10)
