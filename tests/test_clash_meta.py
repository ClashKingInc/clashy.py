import unittest
import coc

from coc.constants import HV_TROOP_ORDER

import tracemalloc

tracemalloc.start()

class ClashMetaTests(unittest.TestCase):

    def test_load_default(self):
        client = coc.Client(load_game_data=coc.LoadGameData(default=True))
        client._load_static()

        self.assertTrue(client._static_data)
        self.assertTrue(client._name_to_id_mapping)
        self.assertIsNotNone(client.get_troop("Barbarian"))

    def test_load_startup_only(self):
        client = coc.Client(load_game_data=coc.LoadGameData(startup_only=True))
        client._load_static()

        self.assertTrue(client._static_data)
        self.assertTrue(client._name_to_id_mapping)

        troop = client.get_troop("Barbarian")
        self.assertIsInstance(troop, coc.Troop)

    def test_troop(self):
        client = coc.Client()
        client._load_static()
        barb = client.get_troop("Barbarian")
        self.assertIsInstance(barb, coc.Troop)

        self.assertEqual(barb.name, "Barbarian")
        self.assertIsInstance(barb.level, int)
        self.assertEqual(barb.level, 1)


class TroopMeta(unittest.TestCase):
    def setUp(self) -> None:
        self.client = coc.Client()
        self.client._load_static()
        self.troop = self.client.get_troop("Barbarian")

    def test_types(self):
        self.assertIsInstance(self.troop, coc.Troop)

    def test_levels(self):
        self.assertIsInstance(self.troop.level, int)
        self.assertEqual(self.troop.max_level, len(self.troop._static_data["levels"]))
    
    def test_troops(self):
        for troop_name in HV_TROOP_ORDER:
            troop = self.client.get_troop(troop_name)
            self.assertIsInstance(troop, coc.Troop)
            self.assertEqual(troop.name, troop_name)
            self.assertTrue(troop.is_home_base )

            max_level = troop._static_data["levels"][-1]["level"]
            for v in troop._static_data["levels"]:
                level = v["level"]
                level_troop = self.client.get_troop(troop_name, level=level)
                self.assertEqual(level_troop.name, troop_name, f"{level_troop.name} name is wrong")
                self.assertEqual(level_troop.upgrade_cost or 0,
                                 v.get("upgrade_cost", 0) or 0,
                                 f"{level_troop.name} upgrade cost level {level} is wrong")
                self.assertEqual(level_troop.upgrade_time.total_seconds(), v.get("upgrade_time", 0),
                                 f"{level_troop.name} upgrade time level {level} is wrong")
            self.assertEqual(troop.max_level, max_level, f"{troop.name} max level is wrong")
