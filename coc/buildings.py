
from .abc import BaseDataClass, LeveledUnit, LevelManager
from .enums import Resource, VillageType, BuildingType
from .miscmodels import TID, TimeDelta
from .troop import Troop

from functools import lru_cache
from pathlib import Path
from typing import Mapping

import orjson


class SeasonalDefenseModule(LeveledUnit):
    """Represents a Seasonal Defense Module.

    Attributes
    ----------
    id: :class:`int`
        The module's unique identifier.
    name: :class:`str`
        The module's name.
    TID: :class:`TID`
        The module's translation IDs for localization.
    upgrade_resource: :class:`Resource`
        The resource type required to upgrade this module.
    max_level: :class:`int`
        The maximum level this module can be upgraded to.
    build_cost: :class:`int`
        The cost to build/upgrade to this level.
    build_time: :class:`TimeDelta`
        The time required to build/upgrade to this level.
    required_townhall: :class:`int`
        The Town Hall level required to upgrade to this module level.
    ability_data: :class:`dict`
        The ability data for this module.
    
    Note
    ----
    To get the upgrade cost, access the `build_cost` of the next level.
    """

    __slots__ = (
        "id",
        "name",
        "TID",
        "upgrade_resource",
        "max_level",
        "build_cost",
        "build_time",
        "required_townhall",
        "ability_data",
    )

    def __init__(self, data: dict, level: int = 0):
        super().__init__(
            initial_level=level,
            static_data=data
        )
        self.id: int = data["_id"]
        self.name: str = data["name"]
        self.TID: TID = TID(data=data["TID"])
        self.upgrade_resource = Resource(value=data["upgrade_resource"])

        self._load_level_data()

    def _load_level_data(self):
        if not self._static_data:
            return

        try:
            level_data = self._static_data["levels"][self._level - 1]
        except IndexError:
            return

        self.build_cost: int = level_data.get("build_cost")
        self.build_time: TimeDelta = TimeDelta(seconds=level_data.get("build_time"))
        self.required_townhall: int = level_data.get("required_townhall")
        self.ability_data: dict = level_data.get("ability_data")

class SeasonalDefense(BaseDataClass):
    """Represents a Seasonal Defense.

    Attributes
    ----------
    id: :class:`int`
        The defense's unique identifier.
    name: :class:`str`
        The defense's name.
    info: :class:`str`
        Description of the defense.
    TID: :class:`TID`
        The defense's translation IDs for localization.
    modules: List[:class:`SeasonalDefenseModule`]
        The list of modules for this defense.
    level: :class:`int`
        The total level (sum of all module levels).
    """

    __slots__ = (
        "id",
        "name",
        "info",
        "TID",
        "modules",
        "level",
    )

    def __init__(self, data: dict, modules: list[SeasonalDefenseModule]):
        self.id = data["_id"]
        self.name: str = data["name"]
        self.info: str = data["info"]
        self.TID = TID(data=data["TID"])

        self.modules = modules
        self.level = sum(m.level for m in self.modules)

class MergeRequirement:
    """Represents a building merge requirement.

    Attributes
    ----------
    id: :class:`int`
        The building's unique identifier.
    name: :class:`str`
        The building's name.
    geared_up: :class:`bool`
        Whether the building needs to be geared up.
    required_level: :class:`int`
        The required level of the building.
    """

    __slots__ = (
        "id",
        "name",
        "geared_up",
        "required_level",
    )

    def __init__(self, data: dict):
        self.id: int = data["_id"]
        self.name: str = data["name"]
        self.geared_up: bool = data["geared_up"]
        self.required_level: int = data["level"]

class GearUp:
    """Represents a gear up requirement for a building.

    Attributes
    ----------
    required_level: :class:`int`
        The required level to gear up.
    building_id: :class:`int`
        The building ID required for gear up.
    resource: :class:`Resource`
        The resource type required for gear up.
    """

    __slots__ = (
        "required_level",
        "building_id",
        "resource",
    )

    def __init__(self, data: dict):
        self.required_level: int = data["level_required"]
        self.building_id: int = data["building_id"]
        self.resource: Resource = Resource(value=data["resource"])

class TownhallUnlock:
    """Represents a building unlock at a townhall level.

    Attributes
    ----------
    name: :class:`str`
        The name of the unlocked item.
    _id: :class:`int`
        The id of the unlocked building.
    quantity: :class:`int`
        The quantity unlocked.
    """

    __slots__ = (
        "name",
        "_id",
        "quantity",
    )

    def __init__(self, data: dict):
        self.name: str = data["name"]
        self._id: int = data["_id"]
        self.quantity: int = data["quantity"]

@lru_cache(maxsize=1)
def _packaged_troop_data() -> dict[int, dict]:
    # Direct Building construction has no Client/StaticData context. Resolve its
    # requirements from the bundled catalog, once, without network access.
    path = Path(__file__).parent / "static" / "static_data.json"
    with path.open("rb") as source:
        return {troop["_id"]: troop for troop in orjson.loads(source.read())["troops"]}


class BuildingVariant(BaseDataClass):
    """A level-specific building variant, such as Archer Hall at Town Hall 19.

    Attributes
    ----------
    id: :class:`int`
        The variant's unique identifier.
    name: :class:`str`
        The variant's name.
    info: :class:`str`
        The variant's description.
    TID: :class:`TID`
        Translation IDs for the name and description.
    is_owned: Optional[:class:`bool`]
        Whether the account export lists this variant as owned. ``None`` means
        ownership was not included, or this is a static catalog definition.
    required_troop: Optional[:class:`Troop`]
        A separate troop object at the minimum required level, or ``None`` if
        this variant has no troop requirement. This is not the player's troop
        and changing its level does not change the unlock requirement.
    required_troop_level: Optional[:class:`int`]
        The minimum required troop level, independent of required_troop.level.
    """

    __slots__ = (
        "id", "name", "info", "TID", "is_owned", "required_troop",
        "required_troop_level",
    )

    def __init__(self, data: dict, troop_data: Mapping[int, dict] | None = None,
                 is_owned: bool | None = None):
        self.id: int = data["_id"]
        self.is_owned = is_owned
        self.name: str = data["name"]
        self.info: str = data["info"]
        self.TID = TID(data=data["TID"])
        self.required_troop: Troop | None = None
        self.required_troop_level: int | None = None
        requirement = data.get("required_troop")
        if requirement is not None:
            troop_id = requirement["_id"]
            self.required_troop_level = requirement["level"]
            catalog = _packaged_troop_data() if troop_data is None else troop_data
            definition = catalog.get(troop_id)
            if definition is None:
                raise ValueError(
                    f"Building variant {self.id} requires unknown troop {troop_id}"
                )
            self.required_troop = Troop(
                data={}, static_data=definition, level=self.required_troop_level
            )


class TownhallWeapon(LeveledUnit):
    """Represents a Townhall Weapon.

    Attributes
    ----------
    name: :class:`str`
        The weapon's name.
    info: :class:`str`
        Description of the weapon.
    TID: :class:`TID`
        The weapon's translation IDs for localization.
    upgrade_resource: :class:`Resource`
        The resource type required to upgrade this weapon.
    build_cost: :class:`int`
        The cost to build/upgrade to this level.
    build_time: :class:`TimeDelta`
        The time required to build/upgrade to this level.
    strength_weight: :class:`int`
        The matchmaking strength weight of a th weapon
    dps: :class:`int`
        The weapon's damage per second.
    
    Note
    ----
    To get the upgrade cost, access the `build_cost` of the next level.
    """

    __slots__ = (
        "name",
        "info",
        "TID",
        "upgrade_resource",
        "build_cost",
        "build_time",
        "strength_weight",
        "dps",
    )

    def __init__(self, data: dict, level: int = 0):
        super().__init__(
            initial_level=level,
            static_data=data
        )
        self.name: str = data["name"]
        self.info: str = data["info"]
        self.TID: TID = TID(data=data["TID"])
        self.upgrade_resource: Resource = Resource(value=data["upgrade_resource"])
        self.strength_weight: int = data.get("strength_weight", 0)

        self._load_level_data()

    def _load_level_data(self):
        if not self._static_data:
            return

        try:
            level_data = self._static_data["levels"][self._level]
        except IndexError:
            return

        self.build_cost: int = level_data["build_cost"]
        self.build_time = TimeDelta(seconds=level_data["build_time"])
        self.dps: int = level_data["dps"]
        self.strength_weight: int = level_data.get("strength_weight", self.strength_weight)

class Supercharge(LevelManager):
    """Represents a Supercharge for a building.

    Attributes
    ----------
    upgrade_resource: :class:`Resource`
        The resource type required to upgrade this supercharge.
    build_cost: :class:`int`
        The cost to build/upgrade to this level.
    build_time: :class:`TimeDelta`
        The time required to build/upgrade to this level.
    hitpoints_buff: :class:`int`
        The hitpoints buff provided by this supercharge.
    dps_buff: :class:`int`
        The damage per second buff provided by this supercharge.
    
    Note
    ----
    To get the upgrade cost, access the `build_cost` of the next level.
    """

    __slots__ = (
        "upgrade_resource",
        "build_cost",
        "build_time",
        "hitpoints_buff",
        "dps_buff",
    )

    def __init__(self, data: dict, level: int = 0):
        super().__init__(
            initial_level=level,
            static_data=data
        )
        self.upgrade_resource: Resource = Resource(value=data["upgrade_resource"])

        self._load_level_data()

    def _load_level_data(self):
        if not self._static_data:
            return

        try:
            level_data = self._static_data["levels"][self._level - 1]
        except IndexError:
            return

        self.build_cost: int = level_data["build_cost"]
        self.build_time = TimeDelta(seconds=level_data["build_time"])
        self.hitpoints_buff: int = level_data["hitpoints_buff"]
        self.dps_buff: int = level_data["dps_buff"]

class Building(LeveledUnit):
    """Represents a Building.

    Attributes
    ----------
    id: :class:`int`
        The building's unique identifier.
    name: :class:`str`
        The building's name.
    info: :class:`str`
        Description of the building.
    TID: :class:`TID`
        The building's translation IDs for localization.
    type: :class:`BuildingType`
        The type of building.
    upgrade_resource: :class:`Resource`
        The resource type required to upgrade this building.
    village: :class:`VillageType`
        The village type where this building belongs.
    width: :class:`int`
        The width of the building.
    is_home_base: :class:`bool`
        Whether this building belongs to the home village.
    is_builder_base: :class:`bool`
        Whether this building belongs to the builder base.
    is_superchargeable: :class:`bool`
        Whether this building can be supercharged.
    gear_up: Optional[:class:`GearUp`]
        The gear up requirements for this building.
    seasonal_defenses: List[:class:`SeasonalDefense`]
        The list of seasonal defenses for this building (Crafting Station only).
    weapon: Optional[:class:`TownhallWeapon`]
        The townhall weapon (only for townhall).
    build_cost: :class:`int`
        The cost to build/upgrade to this level.
    build_time: :class:`TimeDelta`
        The time required to build/upgrade to this level.
    required_townhall: :class:`int`
        The townhall level required to build/upgrade to this level.
    strength_weight: :class:`int`
        The matchmaking strength weight of a building
    hitpoints: :class:`int`
        The building's hitpoints.
    dps: :class:`int`
        The building's damage per second.
    damage: :class:`int`
        The building's per-attack damage
    attack_range: Optional[:class:`int`]
        The building's attack range
    min_range: Optional[:class:`int`]
        The building's minimum attack range
    supercharge: Optional[:class:`Supercharge`]
        The supercharge for this building.
    merge_requirement: List[:class:`MergeRequirement`]
        The merge requirements for this building.
    unlocks: List[:class:`TownhallUnlock`]
        The unlocks provided by this building (only for townhall).
    variants: Tuple[:class:`BuildingVariant`, ...]
        Variant definitions available at this building's current level.
    
    Note
    ----
    To get the upgrade cost, access the `build_cost` of the next level.
    """

    __slots__ = (
        "_supercharge_level",
        "_weapon_level",
        "id",
        "name",
        "info",
        "TID",
        "type",
        "upgrade_resource",
        "village",
        "width",
        "is_home_base",
        "is_builder_base",
        "is_superchargeable",
        "gear_up",
        "seasonal_defenses",
        "weapon",
        "build_cost",
        "build_time",
        "required_townhall",
        "strength_weight",
        "hitpoints",
        "dps",
        "damage",
        "attack_range",
        "min_range",
        "supercharge",
        "merge_requirement",
        "unlocks",
        "variants",
        "_owned_variant_ids",
        "_troop_data",
    )

    def __init__(self,
         data: dict, level: int = 0, weapon_level: int = 0,
         supercharge_level: int = 0,
         seasonal_defenses: list[SeasonalDefense] = None,
         troop_data: Mapping[int, dict] | None = None,
         owned_variant_ids: tuple[int, ...] | None = None
    ):
        super().__init__(
            initial_level=level,
            static_data=data
        )
        self._troop_data = troop_data
        # Preserve absent versus empty ownership while rebuilding level-specific
        # variants. Ownership never identifies which variant is currently active.
        self._owned_variant_ids = None if owned_variant_ids is None else frozenset(owned_variant_ids)
        self.variants: tuple[BuildingVariant, ...] = ()
        self._supercharge_level = supercharge_level
        self._weapon_level = weapon_level

        self.id: int = data["_id"]
        self.name: str = data["name"]
        self.info: str = data["info"]
        self.TID: TID = TID(data=data["TID"])
        self.type = BuildingType(value=data["type"])
        self.upgrade_resource: Resource = Resource(value=data["upgrade_resource"])
        self.village = VillageType(value=data["village"])

        self.is_home_base: bool = self.village == VillageType.home
        self.is_builder_base: bool = self.village == VillageType.builder_base

        self.width: int = data["width"]
        self.is_superchargeable: bool = data["superchargeable"]

        # for buildings with only one level
        self.strength_weight: int = 0
        # only some buildings
        self.gear_up = None
        if "gear_up" in data:
            self.gear_up = GearUp(data=data["gear_up"])

        self.seasonal_defenses = seasonal_defenses or []
        if "seasonal_defenses" in data and not self.seasonal_defenses:
            # if no seasonal defenses are provided, initialize a set
            seasonal_defenses = []
            for defense_data in data["seasonal_defenses"]:
                modules = []
                for module_data in defense_data["modules"]:
                    modules.append(SeasonalDefenseModule(data=module_data))
                seasonal_defenses.append(SeasonalDefense(data=defense_data, modules=modules))
            self.seasonal_defenses = seasonal_defenses

        self._load_level_data()

    def _load_level_data(self):
        if not self._static_data or not self._static_data["levels"]:
            return

        try:
            level_data = self._static_data["levels"][self._level - 1]
        except IndexError:
            return

        self.variants = tuple(
            BuildingVariant(
                data=variant,
                troop_data=self._troop_data,
                is_owned=(
                    variant["_id"] in self._owned_variant_ids
                    if self._owned_variant_ids is not None else None
                ),
            )
            for variant in level_data.get("variants", ())
        )
        self.weapon: TownhallWeapon | None = None
        if "weapon" in level_data:
            self.weapon = TownhallWeapon(level=self._weapon_level, data=level_data["weapon"])

        self.build_cost: int = level_data["build_cost"]
        self.build_time = TimeDelta(seconds=level_data["build_time"])
        self.required_townhall: int = level_data["required_townhall"]
        self.strength_weight: int = level_data.get("strength_weight", 0)
        self.hitpoints: int = level_data["hitpoints"]
        self.dps: int = level_data.get("dps", 0)
        self.damage: int = level_data.get("damage", 0)
        self.attack_range: int | None = level_data.get("attack_range")
        self.min_range: int | None = level_data.get("min_range")

        self.supercharge: Supercharge | None = None
        if "supercharge" in level_data:
            self.supercharge = Supercharge(level=self._supercharge_level, data=level_data["supercharge"])
        # only select buildings
        self.merge_requirement = [MergeRequirement(m) for m in level_data.get("merge_requirement", [])]

        # only the townhall
        self.unlocks = [TownhallUnlock(u) for u in level_data.get("unlocks", [])]

class Trap(LeveledUnit):
    """Represents a Trap.

    Attributes
    ----------
    id: :class:`int`
        The trap's unique identifier.
    name: :class:`str`
        The trap's name.
    TID: :class:`TID`
        The trap's translation IDs for localization.
    upgrade_resource: :class:`Resource`
        The resource type required to upgrade this trap.
    village: :class:`VillageType`
        The village type where this trap belongs.
    is_home_base: :class:`bool`
        Whether this trap belongs to the home village.
    is_builder_base: :class:`bool`
        Whether this trap belongs to the builder base.
    width: :class:`int`
        The width of the trap.
    is_air_triggerable: :class:`bool`
        Whether this trap can be triggered by air units.
    is_ground_triggerable: :class:`bool`
        Whether this trap can be triggered by ground units.
    damage_radius: :class:`int`
        The damage radius of the trap.
    trigger_radius: :class:`int`
        The trigger radius of the trap.
    build_cost: :class:`int`
        The cost to build/upgrade to this level.
    build_time: :class:`TimeDelta`
        The time required to build/upgrade to this level.
    required_townhall: :class:`int`
        The townhall level required to build/upgrade to this level.
    strength_weight: :class:`int`
        The matchmaking strength weight of a trap
    damage: :class:`int`
        The damage dealt by the trap.
    
    Note
    ----
    To get the upgrade cost, access the `build_cost` of the next level.
    """

    __slots__ = (
        "id",
        "name",
        "TID",
        "upgrade_resource",
        "village",
        "width",
        "is_home_base",
        "is_builder_base",
        "is_air_triggerable",
        "is_ground_triggerable",
        "damage_radius",
        "trigger_radius",
        "build_cost",
        "build_time",
        "required_townhall",
        "strength_weight",
        "damage",
    )

    def __init__(self, data: dict, level: int = 0):
        super().__init__(
            initial_level=level,
            static_data=data
        )
        self.id: int = data["_id"]
        self.name: str = data["name"]
        self.TID: TID = TID(data=data["TID"])

        self.upgrade_resource: Resource = Resource(value=data["upgrade_resource"])
        self.village = VillageType(value=data["village"])
        self.is_home_base: bool = self.village == VillageType.home
        self.is_builder_base: bool = self.village == VillageType.builder_base

        self.width: int = data["width"]
        self.is_air_triggerable: bool = data["air_trigger"]
        self.is_ground_triggerable: bool = data["ground_trigger"]
        self.damage_radius: int = data["damage_radius"]
        self.trigger_radius: int = data["trigger_radius"]


    def _load_level_data(self):
        if not self._static_data or not self._static_data["levels"]:
            return

        try:
            level_data = self._static_data["levels"][self._level - 1]
        except IndexError:
            return

        self.build_cost: int = level_data["build_cost"]
        self.build_time = TimeDelta(seconds=level_data["build_time"])
        self.required_townhall: int = level_data["required_townhall"]
        self.strength_weight: int = level_data["strength_weight"]
        self.damage: int = level_data["damage"]
