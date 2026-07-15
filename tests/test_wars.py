import unittest

from coc.enums import BattleModifier
from coc.wars import ClanWar
from coc.wars import ClanWarLogEntry
from coc.war_attack import WarAttack
from coc.miscmodels import Timestamp


class DummyClient:
    raw_attribute = False


class TestWars(unittest.TestCase):
    def test_state(self):
        data = [
            {"state": "notInWar"},
            {"state": "preparation"},
            {"state": "inWar"},
            {"state": "warEnded"},
            {},
        ]
        for case in data:
            war = ClanWar(data=case, clan_tag="", client=None)
            try:
                state = case["state"]
                self.assertIsInstance(state, str)
            except KeyError:
                state = None
                self.assertIsNone(war.state)
            self.assertEqual(war.state, state)

    def test_team_size(self):
        data = [{"teamSize": 15}, {"teamSize": 30}, {"teamSize": 5}, {}]
        for case in data:
            war = ClanWar(data=case, clan_tag="", client=None)
            try:
                size = case["teamSize"]
                self.assertIsInstance(war.team_size, int)
            except KeyError:
                size = 0
                self.assertEqual(war.team_size, 0)
            self.assertEqual(war.team_size, size)

    def test_start_times(self):
        data = [
            {
                "preparationStartTime": "20200522T051229.000Z",
                "startTime": "20200523T043025.000Z",
                "endTime": "20200524T043025.000Z",
            },
        ]
        for case in data:
            war = ClanWar(data=case, clan_tag="", client=None)

            self.assertGreater(war.start_time, war.preparation_start_time)
            self.assertGreater(war.end_time, war.start_time)

            self.assertLess(war.preparation_start_time, war.start_time)
            self.assertLess(war.start_time, war.end_time)

            self.assertIsInstance(war.preparation_start_time, Timestamp)
            self.assertIsInstance(war.start_time, Timestamp)
            self.assertIsInstance(war.end_time, Timestamp)

            self.assertEqual(war.type, "random")

    def test_war_attack_duration(self):
        attack = WarAttack(
            data={
                "stars": 3,
                "destructionPercentage": 100,
                "order": 1,
                "attackerTag": "#AAA",
                "defenderTag": "#BBB",
                "duration": 145,
            },
            client=DummyClient(),
            war=object(),
        )

        self.assertEqual(attack.duration, 145)

    def test_battle_modifier(self):
        cases = {
            "none": BattleModifier.none,
            "hardMode": BattleModifier.hard_mode,
            "minusOne": BattleModifier.minus_one,
            "minusTwo": BattleModifier.minus_two,
            "minusThree": BattleModifier.minus_three,
        }

        for value, expected in cases.items():
            war = ClanWar(data={"battleModifier": value}, clan_tag="", client=None)
            self.assertEqual(war.battle_modifier, expected)
            self.assertEqual(war.battle_modifier.value, value)

    def test_battle_modifier_defaults_to_none(self):
        war = ClanWar(data={}, clan_tag="", client=None)

        self.assertEqual(war.battle_modifier, BattleModifier.none)

    def test_war_log_entry_battle_modifier(self):
        entry = ClanWarLogEntry(data={"battleModifier": "minusThree"}, client=None)

        self.assertEqual(entry.battle_modifier, BattleModifier.minus_three)


class TestWarClan(unittest.TestCase):
    def test_level(self):
        data = {"clan": {"clanLevel": 10}}
        war = ClanWar(data=data, client=None, clan_tag=None)
        self.assertIsInstance(war.clan.level, int)

    def test_destruction(self):
        data = {"clan": {"destructionPercentage": 84.88}}
        war = ClanWar(data=data, client=None, clan_tag=None)
        self.assertIsInstance(war.clan.destruction, float)

    def test_exp_earned(self):
        data = {"clan": {"clanLevel": 10}}
        war = ClanWar(data=data, client=None, clan_tag=None)
        self.assertIsInstance(war.clan.level, int)

    def test_clan_level(self):
        data = {"clan": {"clanLevel": 10}}
        war = ClanWar(data=data, client=None, clan_tag=None)
        self.assertIsInstance(war.clan.level, int)

    def test_clan_level(self):
        data = {"clan": {"clanLevel": 10}}
        war = ClanWar(data=data, client=None, clan_tag=None)
        self.assertIsInstance(war.clan.level, int)

    def test_clan_level(self):
        data = {"clan": {"clanLevel": 10}}
        war = ClanWar(data=data, client=None, clan_tag=None)
        self.assertIsInstance(war.clan.level, int)

    def test_clan_level(self):
        data = {"clan": {"clanLevel": 10}}
        war = ClanWar(data=data, client=None, clan_tag=None)
        self.assertIsInstance(war.clan.level, int)
