import unittest

import coc


class TestEnums(unittest.TestCase):
    def test_role_values(self):
        self.assertEqual(coc.Role.values(), ["member", "admin", "coLeader", "leader"])
        self.assertEqual(coc.Role.names(), ["member", "elder", "co_leader", "leader"])
        self.assertEqual(str(coc.Role.elder), "Elder")
        self.assertEqual(coc.Role.co_leader.in_game_name, "Co-Leader")

    def test_extended_enum_string_comparison(self):
        self.assertEqual(coc.Role.leader, "leader")
        self.assertEqual(coc.Role.co_leader, "coLeader")
        self.assertEqual(coc.Role.co_leader, "co_leader")
        self.assertNotEqual(coc.Role.member, "leader")

    def test_war_enums(self):
        self.assertEqual(str(coc.WarRound.current_war), "current_war")
        self.assertEqual(coc.WarRound.current_war.in_game_name, "Current War")
        self.assertEqual(str(coc.WarState.not_in_war), "Not in War")
        self.assertEqual(coc.WarState.war_ended.in_game_name, "War Ended")
        self.assertEqual(coc.BattleModifier.hard_mode.value, "hardMode")
        self.assertEqual(coc.BattleModifier.minus_one.value, "minusOne")
        self.assertEqual(coc.BattleModifier.minus_three.in_game_name, "Minus Three")

    def test_clan_type(self):
        self.assertEqual(coc.ClanType.open.value, "open")
        self.assertEqual(str(coc.ClanType.invite_only), "Invite Only")
        self.assertEqual(coc.ClanType.invite_only, "inviteOnly")

    def test_player_house_element_type(self):
        self.assertEqual(coc.PlayerHouseElementType.deco.value, "decoration")
        self.assertEqual(str(coc.PlayerHouseElementType.deco), "Decoration")
        self.assertEqual(coc.PlayerHouseElementType.walls.in_game_name, "Walls")

    def test_enums_without_in_game_name_fall_back_to_value(self):
        self.assertEqual(str(coc.Resource.dark_elixir), "Dark Elixir")
        self.assertEqual(str(coc.VillageType.builder_base), "builderBase")


if __name__ == "__main__":
    unittest.main()
