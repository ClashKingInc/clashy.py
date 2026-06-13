from __future__ import annotations

from typing import Optional

import pendulum

from .miscmodels import TIMESTAMP_FORMAT


def _parse_datetime(value: str | None) -> Optional[pendulum.DateTime]:
    if not value:
        return None
    try:
        return pendulum.from_format(value, TIMESTAMP_FORMAT, tz="UTC")
    except ValueError:
        return None


class BattleLogResource:
    """Represents a resource amount in a player battle log entry."""

    __slots__ = ("name", "amount")

    def __init__(self, *, data):
        self.name: str = data.get("name")
        self.amount: int = data.get("amount")

    def __repr__(self):
        return "<%s name=%r amount=%r>" % (self.__class__.__name__, self.name, self.amount)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name and self.amount == other.amount


class BattleLogEntry:
    """Represents a single player battle log entry."""

    __slots__ = (
        "battle_type",
        "attack",
        "timestamp",
        "army_share_code",
        "opponent_player_tag",
        "stars",
        "destruction_percentage",
        "looted_resources",
        "extra_looted_resources",
        "available_loot",
        "_client",
        "_response_retry",
        "_raw_data",
    )

    def __init__(self, *, data, client=None, **_):
        self._client = client
        self._response_retry = data.get("_response_retry")
        self._raw_data = data if client and client.raw_attribute else None
        self._from_data(data)

    def _from_data(self, data):
        data_get = data.get
        resource_cls = BattleLogResource

        self.battle_type: str = data_get("battleType")
        self.attack: bool = data_get("attack")
        self.timestamp = _parse_datetime(data_get("timestamp"))
        self.army_share_code: str = data_get("armyShareCode")
        self.opponent_player_tag: str = data_get("opponentPlayerTag")
        self.stars: int = data_get("stars")
        self.destruction_percentage: int = data_get("destructionPercentage")
        self.looted_resources = [resource_cls(data=item) for item in data_get("lootedResources", [])]
        self.extra_looted_resources = [resource_cls(data=item) for item in data_get("extraLootedResources", [])]
        self.available_loot = [resource_cls(data=item) for item in data_get("availableLoot", [])]

    def __repr__(self):
        return "<%s battle_type=%r opponent_player_tag=%r stars=%r>" % (
            self.__class__.__name__,
            self.battle_type,
            self.opponent_player_tag,
            self.stars,
        )


class LeagueHistoryEntry:
    """Represents a player league season history entry."""

    __slots__ = (
        "league_season_id",
        "league_trophies",
        "league_tier_id",
        "placement",
        "attack_wins",
        "attack_losses",
        "attack_stars",
        "defense_wins",
        "defense_losses",
        "defense_stars",
        "max_battles",
        "_client",
        "_response_retry",
        "_raw_data",
    )

    def __init__(self, *, data, client=None, **_):
        self._client = client
        self._response_retry = data.get("_response_retry")
        self._raw_data = data if client and client.raw_attribute else None
        self._from_data(data)

    def _from_data(self, data):
        data_get = data.get

        self.league_season_id: int = data_get("leagueSeasonId")
        self.league_trophies: int = data_get("leagueTrophies")
        self.league_tier_id: int = data_get("leagueTierId")
        self.placement: int = data_get("placement")
        self.attack_wins: int = data_get("attackWins")
        self.attack_losses: int = data_get("attackLosses")
        self.attack_stars: int = data_get("attackStars")
        self.defense_wins: int = data_get("defenseWins")
        self.defense_losses: int = data_get("defenseLosses")
        self.defense_stars: int = data_get("defenseStars")
        self.max_battles: int = data_get("maxBattles")

    def __repr__(self):
        return "<%s league_season_id=%r league_tier_id=%r placement=%r>" % (
            self.__class__.__name__,
            self.league_season_id,
            self.league_tier_id,
            self.placement,
        )


class LeagueTierGroupBattleLogEntry:
    """Represents an attack or defense log entry inside a league tier group."""

    __slots__ = (
        "opponent_player_tag",
        "opponent_name",
        "stars",
        "destruction_percentage",
        "trophies",
        "creation_time",
    )

    def __init__(self, *, data):
        data_get = data.get

        self.opponent_player_tag: str = data_get("opponentPlayerTag")
        self.opponent_name: str = data_get("opponentName")
        self.stars: int = data_get("stars")
        self.destruction_percentage: int = data_get("destructionPercentage")
        self.trophies: int = data_get("trophies")
        self.creation_time = _parse_datetime(data_get("creationTime"))


class LeagueTierGroupMember:
    """Represents a member inside a league tier group."""

    __slots__ = (
        "player_tag",
        "player_name",
        "clan_tag",
        "clan_name",
        "league_trophies",
        "attack_win_count",
        "attack_lose_count",
        "defense_win_count",
        "defense_lose_count",
    )

    def __init__(self, *, data):
        data_get = data.get

        self.player_tag: str = data_get("playerTag")
        self.player_name: str = data_get("playerName")
        self.clan_tag: str = data_get("clanTag")
        self.clan_name: str = data_get("clanName")
        self.league_trophies: int = data_get("leagueTrophies")
        self.attack_win_count: int = data_get("attackWinCount")
        self.attack_lose_count: int = data_get("attackLoseCount")
        self.defense_win_count: int = data_get("defenseWinCount")
        self.defense_lose_count: int = data_get("defenseLoseCount")


class LeagueTierGroup:
    """Represents a league tier group for one player and league season."""

    __slots__ = (
        "members",
        "attack_logs",
        "defense_logs",
        "_client",
        "_response_retry",
        "_raw_data",
    )

    def __init__(self, *, data, client=None, **_):
        self._client = client
        self._response_retry = data.get("_response_retry")
        self._raw_data = data if client and client.raw_attribute else None
        self._from_data(data)

    def _from_data(self, data):
        self.members = [LeagueTierGroupMember(data=item) for item in data.get("members", [])]
        self.attack_logs = [LeagueTierGroupBattleLogEntry(data=item) for item in data.get("attackLogs", [])]
        self.defense_logs = [LeagueTierGroupBattleLogEntry(data=item) for item in data.get("defenseLogs", [])]

    def __repr__(self):
        return "<%s members=%r attack_logs=%r defense_logs=%r>" % (
            self.__class__.__name__,
            len(self.members),
            len(self.attack_logs),
            len(self.defense_logs),
        )
