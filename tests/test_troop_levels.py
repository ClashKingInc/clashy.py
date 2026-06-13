import unittest
import coc

from coc.constants import SIEGE_MACHINE_ORDER
from tests.mock_api import load_mock_api


class TestTroopLevel(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.coc_client = coc.Client()
        self.coc_client._load_static()
        self.player = load_mock_api("/players/%232PP")

    def test_siege_machines(self):
        machines = [troop for troop in self.player["troops"] if troop["name"] in SIEGE_MACHINE_ORDER]
        self.assertTrue(machines)

        for machine in machines:
            machine_obj = self.coc_client.get_troop(name=machine["name"])
            max_level = machine_obj.get_max_level_for_townhall(self.player["townHallLevel"])
            self.assertGreaterEqual(max_level, machine["level"])


if __name__ == '__main__':
    unittest.main()
