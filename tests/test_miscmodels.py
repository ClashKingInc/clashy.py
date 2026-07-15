import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

import pendulum

from coc.battlelogs import BattleLogEntry, LeagueHistoryEntry, LeagueTierGroup
from coc.enums import BattleType
from coc.miscmodels import SeasonWindow
from coc.static import generate_constants
from coc.utils import get_season_by_id, get_season_end, get_season_start


class TestBattlelogModels(unittest.TestCase):

    def test_battlelog_entry(self):
        data = {
            "battleType": "LEGEND",
            "attack": True,
            "battleTimestamp": "20260501T010203.000Z",
            "battleTime": 138,
            "armyShareCode": "u1x1",
            "opponentPlayerTag": "#2PP",
            "opponentName": "Opponent",
            "opponentTownHallLevel": 17,
            "stars": 3,
            "destructionPercentage": 100,
            "lootedResources": [{"name": "Gold", "amount": 5000}],
            "extraLootedResources": [{"name": "Ore", "amount": 10}],
            "availableLoot": [{"name": "Elixir", "amount": 6000}],
        }

        entry = BattleLogEntry(data=data)

        self.assertEqual(entry.battle_type, BattleType.legend)
        self.assertEqual(entry.battle_type, "LEGEND")
        self.assertEqual(entry.timestamp, pendulum.datetime(2026, 5, 1, 1, 2, 3, tz="UTC"))
        self.assertEqual(entry.duration, 138)
        self.assertEqual(entry.opponent_name, "Opponent")
        self.assertEqual(entry.opponent_town_hall_level, 17)
        self.assertEqual(entry.looted_resources[0].name, "Gold")
        self.assertEqual(entry.extra_looted_resources[0].amount, 10)
        self.assertEqual(entry.available_loot[0].name, "Elixir")

    def test_league_history_entry(self):
        data = {
            "leagueSeasonId": "2026-06-02",
            "leagueTrophies": 5500,
            "leagueTierId": 105000033,
            "placement": 12,
            "attackWins": 5,
            "attackLosses": 1,
            "attackStars": 14,
            "defenseWins": 2,
            "defenseLosses": 4,
            "defenseStars": 9,
            "maxBattles": 8,
        }

        entry = LeagueHistoryEntry(data=data)

        self.assertEqual(entry.league_season_id, "2026-06-02")
        self.assertEqual(entry.league_tier_id, 105000033)
        self.assertEqual(entry.attack_stars, 14)
        self.assertEqual(entry.max_battles, 8)

    def test_league_tier_group(self):
        data = {
            "members": [{
                "playerTag": "#2PP",
                "playerName": "Test",
                "clanTag": "#CLAN",
                "clanName": "Clan",
                "leagueTrophies": 5500,
                "attackWinCount": 1,
                "attackLoseCount": 2,
                "defenseWinCount": 3,
                "defenseLoseCount": 4,
            }],
            "attackLogs": [{
                "opponentPlayerTag": "#ABC",
                "opponentName": "Opponent",
                "stars": 2,
                "destructionPercentage": 87,
                "trophies": 20,
                "creationTime": "20260501T010203.000Z",
            }],
            "defenseLogs": [],
        }

        group = LeagueTierGroup(data=data)

        self.assertEqual(group.members[0].player_tag, "#2PP")
        self.assertEqual(group.attack_logs[0].creation_time, pendulum.datetime(2026, 5, 1, 1, 2, 3, tz="UTC"))
        self.assertEqual(group.defense_logs, [])


class TestSeasonWindows(unittest.TestCase):

    def test_legacy_season(self):
        season = get_season_by_id("2025-08")

        self.assertIsInstance(season, SeasonWindow)
        self.assertEqual(season.id, "2025-08")
        self.assertEqual(season.start_time, pendulum.datetime(2025, 7, 28, 5, tz="UTC"))
        self.assertEqual(season.end_time, pendulum.datetime(2025, 8, 25, 5, tz="UTC"))

    def test_cutover_season(self):
        season = get_season_by_id("2025-09")

        self.assertEqual(season.id, "2025-09")
        self.assertEqual(season.start_time, pendulum.datetime(2025, 8, 25, 5, tz="UTC"))
        self.assertEqual(season.end_time, pendulum.datetime(2025, 10, 6, 5, tz="UTC"))

    def test_post_cutover_season(self):
        season = get_season_by_id("2025-10")

        self.assertEqual(season.id, "2025-10")
        self.assertEqual(season.start_time, pendulum.datetime(2025, 10, 6, 5, tz="UTC"))
        self.assertEqual(season.end_time, pendulum.datetime(2025, 11, 3, 5, tz="UTC"))

    def test_compatibility_wrappers(self):
        self.assertEqual(get_season_start(10, 2025), pendulum.datetime(2025, 10, 6, 5, tz="UTC"))
        self.assertEqual(get_season_end(10, 2025), pendulum.datetime(2025, 11, 3, 5, tz="UTC"))


class TestGenerateConstants(unittest.TestCase):

    def test_update_static_files_downloads_and_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            static_path = Path(tmp) / "static_data.json"
            translations_path = Path(tmp) / "translations.json"

            with patch.object(generate_constants, "download_json",
                              side_effect=[b'{"troops":[]}', b'{"TID":{"EN":"Name"}}']) as download:
                generate_constants.update_static_files(
                    static_data_url="https://example.test/static.json",
                    translations_url="https://example.test/translations.json",
                    static_data_path=static_path,
                    translations_path=translations_path,
                )

            self.assertEqual(download.call_count, 2)
            self.assertEqual(static_path.read_text(), '{"troops":[]}')
            self.assertEqual(translations_path.read_text(), '{"TID":{"EN":"Name"}}')

    def test_build_constants_preserves_generated_names(self):
        static_data = {
            "troops": [
                {"name": "Barbarian", "production_building": "Barracks", "village": "home"},
                {"name": "Sneaky Barbarian", "production_building": "Barracks", "village": "home",
                 "super_troop": "Barbarian"},
                {"name": "Battle Machine", "production_building": "Hero Hall", "village": "builderBase"},
            ],
            "spells": [{"name": "Lightning Spell", "upgrade_resource": "Elixir"}],
            "heroes": [{"name": "Barbarian King", "village": "home", "levels": [{"required_townhall": 7}]}],
            "equipment": [{"name": "Barbarian Puppet"}],
            "pets": [{"name": "L.A.S.S.I"}],
            "buildings": [{"name": "Cannon", "village": "home"}],
            "achievements": [{"name": "Bigger Coffers", "village": "home", "ui_priority": 1}],
        }

        constants = generate_constants.build_constants(static_data)

        self.assertEqual(constants["ELIXIR_TROOP_ORDER"], ["Barbarian"])
        self.assertEqual(constants["SUPER_TROOP_ORDER"], ["Sneaky Barbarian"])
        self.assertEqual(constants["HV_TROOP_ORDER"], "ELIXIR_TROOP_ORDER + DARK_ELIXIR_TROOP_ORDER")
