import json
import unittest

from pathlib import Path

from coc.buildings import Building, SeasonalDefenseModule


STATIC_DATA_PATH = Path(__file__).parent.parent / "coc" / "static" / "static_data.json"


class TestBuildingStaticData(unittest.TestCase):

    def test_seasonal_defense_module_loads_level_townhall_requirement(self):
        module = SeasonalDefenseModule(
            level=2,
            data={
                "_id": 102000001,
                "name": "Seasonal Module",
                "TID": {"name": "TID_SEASONAL_MODULE"},
                "upgrade_resource": "Gold",
                "levels": [
                    {
                        "level": 1,
                        "required_townhall": 12,
                        "build_cost": 0,
                        "build_time": 0,
                        "ability_data": {},
                    },
                    {
                        "level": 2,
                        "required_townhall": 13,
                        "build_cost": 100,
                        "build_time": 60,
                        "ability_data": {},
                    },
                ],
            },
        )

        self.assertEqual(module.required_townhall, 13)
        self.assertEqual(module.get_max_level_for_townhall(12), 1)
        self.assertEqual(module.get_max_level_for_townhall(13), 2)

    @classmethod
    def setUpClass(cls):
        with STATIC_DATA_PATH.open() as fp:
            cls.buildings = json.load(fp)["buildings"]

    def get_building_data(self, name):
        return next(building for building in self.buildings if building["name"] == name)

    def test_building_without_damage_stats_defaults_to_zero(self):
        building = Building(data=self.get_building_data("Air Sweeper"))

        self.assertEqual(building.dps, 0)
        self.assertEqual(building.damage, 0)
        self.assertEqual(building.attack_range, 1500)
        self.assertEqual(building.min_range, 100)

    def test_building_damage_is_separate_from_dps(self):
        building = Building(data=self.get_building_data("Eagle Artillery"))

        self.assertEqual(building.dps, 0)
        self.assertEqual(building.damage, 20)
        self.assertEqual(building.attack_range, 5000)
        self.assertEqual(building.min_range, 700)

    def test_missing_building_ranges_are_none(self):
        building = Building(data=self.get_building_data("Army Camp"))

        self.assertIsNone(building.attack_range)
        self.assertIsNone(building.min_range)

    def test_all_generated_building_levels_load(self):
        for building_data in self.buildings:
            building = Building(data=building_data)
            for level_data in building_data.get("levels", []):
                with self.subTest(building=building.name, level=level_data["level"]):
                    building.level = level_data["level"]
