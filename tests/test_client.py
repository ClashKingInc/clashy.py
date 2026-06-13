import unittest

import coc

from coc.battlelogs import BattleLogEntry, LeagueHistoryEntry, LeagueTierGroup
from coc.http import HTTPClient, Route


class FakeHTTP:
    def __init__(self):
        self.calls = []

    async def get_player_battlelog(self, player_tag, **kwargs):
        self.calls.append(("get_player_battlelog", player_tag, kwargs))
        return {"items": [{"battleType": "legendLeague", "opponentPlayerTag": "#ABC", "stars": 3}]}

    async def get_player_league_history(self, player_tag, **kwargs):
        self.calls.append(("get_player_league_history", player_tag, kwargs))
        return {"items": [{"leagueSeasonId": 202605, "leagueTierId": 105000033}]}

    async def get_player_league_group(self, player_tag, league_group_tag, league_season_id, **kwargs):
        self.calls.append(("get_player_league_group", player_tag, league_group_tag, league_season_id, kwargs))
        return {
            "members": [{"playerTag": player_tag, "playerName": "Test"}],
            "attackLogs": [],
            "defenseLogs": [],
        }

    async def search_league_tiers(self, **kwargs):
        self.calls.append(("search_league_tiers", kwargs))
        return {"items": [{"id": 105000033, "name": "Electro League 33", "iconUrls": {}}]}

    async def get_league_tier(self, league_id, **kwargs):
        self.calls.append(("get_league_tier", league_id, kwargs))
        return {"id": league_id, "name": "Electro League 33", "iconUrls": {}}


class TestClientNewEndpoints(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = coc.Client()
        self.client.http = FakeHTTP()

    async def test_get_player_battlelog(self):
        entries = await self.client.get_player_battlelog("2pp")

        self.assertEqual(self.client.http.calls[0][1], "#2PP")
        self.assertIsInstance(entries[0], BattleLogEntry)
        self.assertEqual(entries[0].stars, 3)

    async def test_get_player_league_history(self):
        entries = await self.client.get_player_league_history("2pp")

        self.assertEqual(self.client.http.calls[0][1], "#2PP")
        self.assertIsInstance(entries[0], LeagueHistoryEntry)
        self.assertEqual(entries[0].league_tier_id, 105000033)

    async def test_get_player_league_group(self):
        group = await self.client.get_player_league_group("2pp", "abc", 202605)

        self.assertEqual(self.client.http.calls[0][1:4], ("#2PP", "#ABC", 202605))
        self.assertIsInstance(group, LeagueTierGroup)
        self.assertEqual(group.members[0].player_tag, "#2PP")

    async def test_league_tier_methods(self):
        tiers = await self.client.search_league_tiers()
        tier = await self.client.get_league_tier(105000033)

        self.assertEqual(tiers[0].id, 105000033)
        self.assertEqual(tier.name, "Electro League 33")


class TestHTTPNewRoutes(unittest.IsolatedAsyncioTestCase):

    async def test_player_league_group_route(self):
        http = object.__new__(HTTPClient)
        http.base_url = "https://api.example.test/v1"
        captured = {}

        async def request(route, **kwargs):
            captured["route"] = route
            captured["kwargs"] = kwargs
            return {}

        http.request = request

        await http.get_player_league_group("#2PP", "#GROUP", 202605, lookup_cache=True)

        self.assertEqual(captured["route"].url,
                         "https://api.example.test/v1/leaguegroup/%23GROUP/202605?playerTag=%232PP")
        self.assertTrue(captured["kwargs"]["lookup_cache"])

    def test_route_encodes_hash_in_path_and_query(self):
        route = Route("GET", "https://api.example.test/v1", "/players/#2PP/battlelog", playerTag="#ABC")

        self.assertEqual(route.url, "https://api.example.test/v1/players/%232PP/battlelog?playerTag=%23ABC")
