import unittest

from coc.clans import Clan
from coc.miscmodels import Location, Label, BaseLeague, ChatLanguage, CapitalDistrict
from coc.players import ClanMember
from tests.mock_api import load_mock_api

import tracemalloc

tracemalloc.start()

MOCK_CLAN = load_mock_api("/clans/%232PP")
MOCK_SEARCH_CLAN = load_mock_api("/clans?name=test")


class TestClans(unittest.TestCase):
	def test_points(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.points, MOCK_CLAN["clanPoints"])

	def test_member_count(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.member_count, MOCK_CLAN["members"])
		self.assertEqual(len(clan.members), len(MOCK_CLAN["memberList"]))

	def test_location(self):
		location = Location(data=MOCK_CLAN["location"])
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.location, location)
		self.assertEqual(clan.location.id, location.id)

	def test_type(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.type, MOCK_CLAN["type"])

	def test_required_trophies(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.required_trophies, MOCK_CLAN["requiredTrophies"])

	def test_war_frequency(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.war_frequency, MOCK_CLAN["warFrequency"])

	def test_war_win_streak(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.war_win_streak, MOCK_CLAN["warWinStreak"])

	def test_war_wins(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.war_wins, MOCK_CLAN["warWins"])

	def test_war_ties(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.war_ties, MOCK_CLAN.get("warTies", -1))

	def test_war_losses(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.war_losses, MOCK_CLAN.get("warLosses", -1))

	def test_public_war_log(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.public_war_log, MOCK_CLAN["isWarLogPublic"])
		self.assertIsInstance(clan.public_war_log, bool)

	def test_description(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertEqual(clan.description, MOCK_CLAN["description"])
		self.assertIsInstance(clan.description, str)

	def test_war_league(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		war_league = BaseLeague(data=MOCK_CLAN["warLeague"])
		self.assertEqual(clan.war_league, war_league)
		self.assertIsInstance(clan.war_league, BaseLeague)
		self.assertIsInstance(clan.war_league.id, int)
		self.assertIsInstance(clan.war_league.name, str)

	def test_labels(self):
		clan = Clan(data=MOCK_CLAN, client=None)
		self.assertIsInstance(clan.labels, list)

		label_ids = MOCK_CLAN["labels"]
		for index, label in enumerate(clan.labels):
			mock_label = Label(data=label_ids[index], client=None)
			self.assertEqual(label, mock_label)
			self.assertIsInstance(label.id, int)
			self.assertIsInstance(label.name, str)
			self.assertIsInstance(str(label), str)

	def test_members(self):
		clan = Clan(data=MOCK_CLAN, client=None)

		self.assertEqual(clan.member_count, len(clan.members))
		self.assertIsInstance(clan.members, list)

		for member in clan.members:
			self.assertIsInstance(member, ClanMember)

			get_member = clan.get_member(member.tag)
			self.assertEqual(member, get_member)

			by_name = clan.get_member_by(name=member.name, trophies=member.trophies)
			self.assertEqual(member, by_name)

	def test_clans_all_attributes(self):
		data = MOCK_CLAN
		clan = Clan(data=data, client=None)
		map_raw_to_cocpy = {"tag"  : "tag", "name": "name", "type": "type", "description": "description",
			"isFamilyFriendly"     : "family_friendly", "clanLevel": "level", "clanPoints": "points",
			"clanBuilderBasePoints": "builder_base_points", "clanCapitalPoints": "capital_points",
			"requiredTrophies"     : "required_trophies", "warFrequency": "war_frequency",
			"warWinStreak"         : "war_win_streak", "warWins": "war_wins", "isWarLogPublic": "public_war_log",
			"members"              : "member_count", "requiredBuilderBaseTrophies": "required_builder_base_trophies",
			"requiredTownhallLevel": "required_townhall"}

		for k, v in map_raw_to_cocpy.items():
			self.assertEqual(data.get(k), clan.__getattribute__(v))

		# test all non trivial attributes

		# test members
		self.assertIsInstance(clan.members, list)
		for member in clan.members:
			self.assertIsInstance(member, ClanMember)

			get_member = clan.get_member(member.tag)
			self.assertEqual(member, get_member)

			by_name = clan.get_member_by(name=member.name, trophies=member.trophies)
			self.assertEqual(member, by_name)

		# test labels
		self.assertIsInstance(clan.labels, list)
		label_data = data.get("labels")
		for index in range(len(label_data)):
			mock_label = Label(data=label_data[index], client=None)
			self.assertEqual(clan.labels[index], mock_label)
			self.assertIsInstance(clan.labels[index].id, int)
			self.assertIsInstance(clan.labels[index].name, str)
			self.assertIsInstance(str(clan.labels[index]), str)

		# test chat language
		self.assertIsInstance(clan.chat_language, ChatLanguage)
		self.assertEqual(clan.chat_language.id, data.get("chatLanguage", {}).get("id"))
		self.assertEqual(clan.chat_language.name, data.get("chatLanguage", {}).get("name"))
		self.assertEqual(clan.chat_language.language_code, data.get("chatLanguage", {}).get("languageCode"))

		# test badges
		self.assertEqual(clan.badge.small, data.get("badgeUrls", {}).get("small"))
		self.assertEqual(clan.badge.medium, data.get("badgeUrls", {}).get("medium"))
		self.assertEqual(clan.badge.url, data.get("badgeUrls", {}).get("medium"))
		self.assertEqual(clan.badge.large, data.get("badgeUrls", {}).get("large"))

		# test capital league
		c_league = BaseLeague(data=data["capitalLeague"])
		self.assertEqual(clan.capital_league, c_league)
		self.assertIsInstance(clan.capital_league, BaseLeague)
		self.assertIsInstance(clan.capital_league.id, int)
		self.assertIsInstance(clan.capital_league.name, str)

		# test war league
		war_league = BaseLeague(data=data["warLeague"])
		self.assertEqual(clan.war_league, war_league)
		self.assertIsInstance(clan.war_league, BaseLeague)
		self.assertIsInstance(clan.war_league.id, int)
		self.assertIsInstance(clan.war_league.name, str)

		# test location
		location = Location(data=data["location"])
		self.assertEqual(clan.location, location)
		self.assertEqual(clan.location.id, location.id)

		# test capital districts
		district_data = data.get("clanCapital", {}).get("districts", [])
		for index in range(len(district_data)):
			mock_district = CapitalDistrict(data=district_data[index], client=None)
			self.assertEqual(clan.capital_districts[index], mock_district)
			self.assertIsInstance(clan.capital_districts[index].id, int)
			self.assertIsInstance(clan.capital_districts[index].name, str)
			self.assertIsInstance(str(clan.capital_districts[index]), str)

	def test_search_all_attributes(self):
		datas = MOCK_SEARCH_CLAN["items"]
		for data in datas:
			clan = Clan(data=data, client=None)
			map_raw_to_cocpy = {"tag"        : "tag", "name": "name", "type": "type", "description": "description",
				"isFamilyFriendly"           : "family_friendly", "clanLevel": "level", "clanPoints": "points",
				"clanBuilderBasePoints"      : "builder_base_points", "clanCapitalPoints": "capital_points",
				"requiredTrophies"           : "required_trophies", "warFrequency": "war_frequency",
				"warWinStreak"               : "war_win_streak", "warWins": "war_wins",
				"isWarLogPublic"             : "public_war_log", "members": "member_count",
				"requiredBuilderBaseTrophies": "required_builder_base_trophies",
				"requiredTownhallLevel"      : "required_townhall"}

			for k, v in map_raw_to_cocpy.items():
				self.assertEqual(data.get(k), clan.__getattribute__(v))

			# test all non trivial attributes

			# test members
			self.assertIsInstance(clan.members, list)
			for member in clan.members:
				self.assertIsInstance(member, ClanMember)

				get_member = clan.get_member(member.tag)
				self.assertEqual(member, get_member)

				by_name = clan.get_member_by(name=member.name, trophies=member.trophies)
				self.assertEqual(member, by_name)

			# test labels
			self.assertIsInstance(clan.labels, list)
			label_data = data.get("labels", [])
			for index in range(len(label_data)):
				mock_label = Label(data=label_data[index], client=None)
				self.assertEqual(clan.labels[index], mock_label)
				self.assertIsInstance(clan.labels[index].id, int)
				self.assertIsInstance(clan.labels[index].name, str)
				self.assertIsInstance(str(clan.labels[index]), str)

			# test chat language
			if data.get("chatLanguage"):
				self.assertIsInstance(clan.chat_language, ChatLanguage)
				self.assertEqual(clan.chat_language.id, data.get("chatLanguage", {}).get("id"))
				self.assertEqual(clan.chat_language.name, data.get("chatLanguage", {}).get("name"))
				self.assertEqual(clan.chat_language.language_code, data.get("chatLanguage", {}).get("languageCode"))

			# test badges
			self.assertEqual(clan.badge.small, data.get("badgeUrls", {}).get("small"))
			self.assertEqual(clan.badge.medium, data.get("badgeUrls", {}).get("medium"))
			self.assertEqual(clan.badge.url, data.get("badgeUrls", {}).get("medium"))
			self.assertEqual(clan.badge.large, data.get("badgeUrls", {}).get("large"))

			# test capital league
			c_league = BaseLeague(data=data["capitalLeague"])
			self.assertEqual(clan.capital_league, c_league)
			self.assertIsInstance(clan.capital_league, BaseLeague)
			self.assertIsInstance(clan.capital_league.id, int)
			self.assertIsInstance(clan.capital_league.name, str)

			# test war league
			war_league = BaseLeague(data=data["warLeague"])
			self.assertEqual(clan.war_league, war_league)
			self.assertIsInstance(clan.war_league, BaseLeague)
			self.assertIsInstance(clan.war_league.id, int)
			self.assertIsInstance(clan.war_league.name, str)

			# test location
			if data.get("location"):
				location = Location(data=data["location"])
				self.assertEqual(clan.location, location)
				self.assertEqual(clan.location.id, location.id)
			else:
				self.assertIsNone(clan.location)

			# test capital districts
			district_data = data.get("clanCapital", {}).get("districts", [])
			for index in range(len(district_data)):
				mock_district = CapitalDistrict(data=district_data[index], client=None)
				self.assertEqual(clan.capital_districts[index], mock_district)
				self.assertIsInstance(clan.capital_districts[index].id, int)
				self.assertIsInstance(clan.capital_districts[index].name, str)
				self.assertIsInstance(str(clan.capital_districts[index]), str)
