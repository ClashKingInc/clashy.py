
import inspect
import re

from collections import deque, UserDict
from functools import wraps
from operator import attrgetter
from typing import Any, Callable, Generic, Iterable, List, Optional, Type, TypeVar, Union

import pendulum

from .miscmodels import SeasonWindow

TAG_VALIDATOR = re.compile(r"^#?[PYLQGRJCUV0289]+$")
SEASON_CUTOFF_START = pendulum.datetime(2025, 8, 25, 5, 0, 0, tz="UTC")
SEASON_CUTOFF_END = pendulum.datetime(2025, 10, 6, 5, 0, 0, tz="UTC")
SEASON_DURATION_DAYS = 28
SEASON_DURATION_SECONDS = SEASON_DURATION_DAYS * 24 * 60 * 60

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)


def find(predicate: Callable[[T], Any], iterable: Iterable[T]) -> Optional[T]:
    """A helper to return the first element found in the sequence
    that meets the predicate.

    For example: ::

        leader = coc.utils.find(lambda m: m.trophies > 5000, clan.members)

    would find the first :class:`~coc.ClanMember` who has more than 5000 trophies and return it.
    If no members have more than 5000 trophies, then ``None`` is returned.

    Parameters
    -----------
    predicate
        A function that returns a boolean-like result.
    iterable: iterable
        The iterable to search through.

    Returns
    -------
    The first item in the iterable which matches the predicate passed.
    """
    for element in iterable:
        if predicate(element):
            return element
    return None


def get(iterable: Iterable[T], **attrs: Any) -> Optional[T]:
    r"""A helper that returns the first item in an iterable that matches the attributes passed.

    If no match is found, ``None`` is returned.

    Example
    -------
    .. code-block:: python3

        member = utils.get(clan.members, level=100, name="Mathsman")
        # returns the first member who has the name "Mathsman" and is level 100

        member = utils.get(clan.members, role=coc.Role.leader)
        # returns the clan leader

        label = utils.get(player.labels, name="Competitive")
        # returns the player's label if they have Competitive.

    Parameters
    ----------
    iterable: iterable
        The list of items to match the attributes from
    \*\*attrs
        A series of kwargs that specify which attributes to match.

    Returns
    -------
    The object from the iterable that matches the attributes passed, or ``None`` if not found.
    """
    converted = [(attrgetter(attr), value) for attr, value in attrs.items()]
    for elem in iterable:
        if all(pred(elem) == value for pred, value in converted):
            return elem
    return None


def is_valid_tag(tag: str) -> bool:
    """Validates that a string is a valid Clash of Clans tag.

    This uses the assumption that tags can only consist of the characters PYLQGRJCUV0289.

    Example
    -------

    .. code-block:: python3

        from coc import utils

        user_input = input("Please enter a tag")

        if utils.is_valid_tag(user_input) is True:
            print("{} is a valid tag".format(user_input))
        else:
            print("{} is not a valid tag".format(user_input))

    Returns
    -------
    :class:`bool`
        Whether the tag is a valid tag.
    """
    if TAG_VALIDATOR.match(correct_tag(tag)):
        return True
    return False


def correct_tag(tag: str, prefix: str = "#") -> str:
    """Attempts to correct malformed Clash of Clans tags
    to match how they are formatted in game

    Example
    -------

    .. code-block:: python3

            new_tag = utils.correct_tag(" 123aBc O")
            # new_tag is "#123ABC0".


    Parameters
    ----------
    tag: str
        The tag to correct.
    prefix: str
        The prefix to insert at the start of the tag. Defaults to ``#``.

    Returns
    -------
    str
        The corrected tag.
    """
    return tag and prefix + re.sub(r"[^A-Z0-9]+", "", tag.upper()).replace("O", "0")


def corrected_tag() -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Helper decorator to fix tags passed into client calls. The tag must be the first parameter."""

    def deco(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            self = args[0]

            if not self.correct_tags:
                return func(*args, **kwargs)

            args = list(args)
            args[1] = correct_tag(args[1])
            return func(*tuple(args), **kwargs)

        return wrapper

    return deco


def maybe_sort(
        seq: Iterable[T], sort: bool, itr: bool = False, key: Callable[[str], Any] = attrgetter("order")
) -> Union[List[T], Iterable[T]]:
    """Returns list or iter based on itr if sort is false otherwise sorted
    with key defaulting to operator.attrgetter('order')
    """
    return (list, iter)[itr](n for n in sorted(seq, key=key)) if sort else (list, iter)[itr](n for n in seq)


def item(
    _object,
    *,
    index: bool = False,
    index_type: Union[int, str] = 0,
    attribute: str = None,
    index_before_attribute: bool = True
):
    """Returns an object, an index, and/or an attribute of the object."""
    attr_get = attrgetter(attribute or "")
    if not (index or index_type or attribute):
        return _object
    if (index or index_type) and not attribute:
        return _object[index_type]
    if attribute and not (index or index_type):
        return attr_get(_object)
    if index_before_attribute:
        return attr_get(_object[index_type])
    return attr_get(_object)[index_type]


def custom_isinstance(obj, module, name):
    """Helper utility to do an `isinstance` check without importing the module (circular imports)"""
    # pylint: disable=broad-except
    for cls in inspect.getmro(type(obj)):
        try:
            if cls.__module__ == module and cls.__name__ == name:
                return True
        except Exception:
            pass
    return False


async def maybe_coroutine(function_, *args, **kwargs):
    """Returns the result of a function which may or may not be a coroutine."""
    value = function_(*args, **kwargs)
    if inspect.isawaitable(value):
        return await value

    return value


def _last_monday_at_five_utc(year: int, month: int) -> pendulum.DateTime:
    if month == 12:
        next_month = pendulum.datetime(year + 1, 1, 1, 5, 0, 0, tz="UTC")
    else:
        next_month = pendulum.datetime(year, month + 1, 1, 5, 0, 0, tz="UTC")
    last_day = next_month.subtract(days=1)
    return last_day.subtract(days=last_day.day_of_week)


def _old_season_end(timestamp: pendulum.DateTime) -> pendulum.DateTime:
    end_time = _last_monday_at_five_utc(timestamp.year, timestamp.month)
    if timestamp >= end_time:
        if timestamp.month == 12:
            return _last_monday_at_five_utc(timestamp.year + 1, 1)
        return _last_monday_at_five_utc(timestamp.year, timestamp.month + 1)
    return end_time


def _old_season_start_from_end(end_time: pendulum.DateTime) -> pendulum.DateTime:
    if end_time.month == 1:
        return _last_monday_at_five_utc(end_time.year - 1, 12)
    return _last_monday_at_five_utc(end_time.year, end_time.month - 1)


def _parse_season_id(season_id: str) -> tuple[int, int]:
    try:
        year_text, month_text = season_id.split("-", maxsplit=1)
        year, month = int(year_text), int(month_text)
    except ValueError as exception:
        raise ValueError(f"invalid season id {season_id!r}") from exception
    if not 1 <= month <= 12:
        raise ValueError(f"invalid season id {season_id!r}")
    return year, month


def _season_window_for_timestamp(timestamp=None):
    target = pendulum.now("UTC") if timestamp is None else pendulum.instance(timestamp, tz="UTC")

    if target < SEASON_CUTOFF_START:
        end_time = _old_season_end(target)
        return SeasonWindow(
            id=end_time.strftime("%Y-%m"),
            start_time=_old_season_start_from_end(end_time),
            end_time=end_time,
        )

    if target < SEASON_CUTOFF_END:
        return SeasonWindow(id="2025-09", start_time=SEASON_CUTOFF_START, end_time=SEASON_CUTOFF_END)

    seasons_passed = int((target.int_timestamp - SEASON_CUTOFF_END.int_timestamp) // SEASON_DURATION_SECONDS)
    start_time = SEASON_CUTOFF_END.add(days=seasons_passed * SEASON_DURATION_DAYS)
    end_time = start_time.add(days=SEASON_DURATION_DAYS)

    total_months = SEASON_CUTOFF_END.year * 12 + (SEASON_CUTOFF_END.month - 1) + seasons_passed
    year = total_months // 12
    month = total_months - year * 12 + 1

    return SeasonWindow(id=f"{year:04d}-{month:02d}", start_time=start_time, end_time=end_time)


def get_season_by_id(season_id: str):
    """Get the Clash of Clans league season window for a ``YYYY-MM`` season ID."""
    if season_id == "2025-09":
        return SeasonWindow(id=season_id, start_time=SEASON_CUTOFF_START, end_time=SEASON_CUTOFF_END)

    year, month = _parse_season_id(season_id)
    ref_total_months = SEASON_CUTOFF_END.year * 12 + (SEASON_CUTOFF_END.month - 1)
    target_total_months = year * 12 + (month - 1)
    seasons_passed = target_total_months - ref_total_months

    if seasons_passed < 0:
        end_time = _last_monday_at_five_utc(year, month)
        return SeasonWindow(id=season_id, start_time=_old_season_start_from_end(end_time), end_time=end_time)

    start_time = SEASON_CUTOFF_END.add(days=seasons_passed * SEASON_DURATION_DAYS)
    return SeasonWindow(id=season_id, start_time=start_time, end_time=start_time.add(days=SEASON_DURATION_DAYS))


def get_season_start(month: Optional[int] = None, year: Optional[int] = None) -> pendulum.DateTime:
    """Get the datetime that the requested season started."""
    if month and year:
        return get_season_by_id(f"{year:04d}-{month:02d}").start_time
    return _season_window_for_timestamp().start_time


def get_season_end(month: Optional[int] = None, year: Optional[int] = None) -> pendulum.DateTime:
    """Get the datetime that the requested season ends."""
    if month and year:
        return get_season_by_id(f"{year:04d}-{month:02d}").end_time
    return _season_window_for_timestamp().end_time


def get_clan_games_start(time: Optional[pendulum.DateTime] = None) -> pendulum.DateTime:
    """Get the datetime that the next clan games will start.

    This goes by the assumption that clan games start at 8am UTC at the 22nd of each month.

    .. note::

        If you want the start of the next or running clan games, do not pass any parameters in,
        for any other pass a pendulum DateTime in the month before.

    Parameters
    ----------
    time: Optional[pendulum.DateTime]
        Some time in the month before the clan games you want the start of.

    Returns
    -------
    clan_games_start: :class:`pendulum.DateTime`
        The start of the next or running clan games.
    """
    time = time or pendulum.now("UTC")
    month = time.month
    year = time.year
    this_months_cg_end = pendulum.datetime(time.year, time.month, 28, 8, 0, 0, tz="UTC")
    if time > this_months_cg_end and month < 12:
        month += 1
    elif time > this_months_cg_end:  # we're at the end of December
        month = 1
        year += 1
    return pendulum.datetime(year, month, 22, 8, 0, 0, tz="UTC")


def get_clan_games_end(time: Optional[pendulum.DateTime] = None) -> pendulum.DateTime:
    """Get the datetime that the next clan games will end.

    This goes by the assumption that clan games end at 8am UTC at the 28th of each month.

    .. note::

        If you want the end of the next or running clan games, do not pass any parameters in,
        for any other pass a pendulum DateTime in the month before.

    Parameters
    ----------
    time: Optional[pendulum.DateTime]
        Some time in the month before the clan games you want the end of.

    Returns
    -------
    clan_games_end: :class:`pendulum.DateTime`
        The end of the next or running clan games.
    """
    time = time or pendulum.now("UTC")
    month = time.month
    year = time.year
    this_months_cg_end = pendulum.datetime(time.year, time.month, 28, 8, 0, 0, tz="UTC")
    if time > this_months_cg_end and month < 12:
        month += 1
    elif time > this_months_cg_end:  # we're in December
        month = 1
        year += 1
    return pendulum.datetime(year, month, 28, 8, 0, 0, tz="UTC")


def get_raid_weekend_start(time: Optional[pendulum.DateTime] = None) -> pendulum.DateTime:
    """Get the datetime that the raid weekend will start.

    This goes by the assumption that raid weekends start at friday 7am UTC.

    .. note::

        If you want the start of the next or running raid weekend, do not pass any parameters in,
        for any other pass a pendulum DateTime in the week before.

    Parameters
    ----------
    time: Optional[pendulum.DateTime]
        Some time in the week before the raid weekend you want the start of.

    Returns
    -------
    raid_weekend_start: :class:`pendulum.DateTime`
        The start of the raid weekend.
    """
    time = time or pendulum.now("UTC")
    time = get_raid_weekend_end(time)
    return time.subtract(days=3)


def get_raid_weekend_end(time: Optional[pendulum.DateTime] = None) -> pendulum.DateTime:
    """Get the datetime that the raid weekend will end.

    This goes by the assumption that raid weekends end at monday 7am UTC.

    .. note::

        If you want the end of the next or running raid weekend, do not pass any parameters in,
        for any other pass a pendulum DateTime in the week before.

    Parameters
    ----------
    time: Optional[pendulum.DateTime]
        Some time in the week before the raid weekend you want the end of.

    Returns
    -------
    raid_weekend_end: :class:`pendulum.DateTime`
        The end of the raid weekend.
    """
    # Shift the time so that we can pretend the raid ends just after midnight
    time = time or pendulum.now("UTC")
    shifted = time.subtract(hours=7, microseconds=1)
    return shifted.add(days=7 - shifted.day_of_week).set(hour=7, minute=0, second=0, microsecond=0)


class _CachedProperty(Generic[T, T_co]):
    def __init__(self, name: str, function: Callable[[T], T_co]) -> None:
        self.name = name
        self.function = function
        self.__doc__ = getattr(function, '__doc__')

    def __get__(self, instance: T, owner: Type[T]) -> T_co:
        try:
            return getattr(instance, self.name)
        except AttributeError:
            result = self.function(instance)
            setattr(instance, self.name, result)
            return result


def cached_property(name: str) -> Callable[[Callable[[T], T_co]], _CachedProperty[T, T_co]]:
    def deco(func: Callable[[T], T_co]) -> _CachedProperty[T, T_co]:
        return _CachedProperty(name, func)
    return deco


class FIFO(UserDict):
    """Implements a FIFO (least-recently-used) dict with a settable max size."""

    __slots__ = (
        "__keys",
        "max_size",
    )

    def __init__(self, max_size):
        self.max_size = max_size
        self.__keys = deque()
        super().__init__()

    def __verify_max_size(self):
        while len(self) > self.max_size:
            del self[self.__keys.popleft()]

    def __setitem__(self, key, value):
        self.__keys.append(key)
        super().__setitem__(key, value)
        self.__verify_max_size()

    def __getitem__(self, key):
        self.__verify_max_size()
        return super().__getitem__(key)

    def __contains__(self, key):
        self.__verify_max_size()
        return super().__contains__(key)

    def copy(self):
        self.data = self.data.copy()
        return self


class HTTPStats(dict):
    """Implements a basic key: deque value to aid with HTTP performance stats."""

    __slots__ = ("max_size",)

    def __init__(self, max_size):
        self.max_size = max_size
        super().__init__()

    def __setitem__(self, key, value):
        try:
            super().__getitem__(key).append(value)
        except (KeyError, AttributeError):
            super().__setitem__(key, deque((value,), maxlen=self.max_size))

    def get_average(self, key):
        """Get the average latency / performance counter for an API endpoint"""
        try:
            stats = self[key]
        except KeyError:
            return None

        return sum(stats) / len(stats)

    def get_mixed_average(self):
        """Get the average latency / performance counter for all API endpoints"""
        stats = [*self.values()]
        return sum(stats) / len(stats)

    def get_all_average(self):
        """Get the average latency / performance counter for each API endpoint."""
        return {k: sum(v) / len(v) for k, v in self.items()}


class CaseInsensitiveDict(dict):
    def __getitem__(self, key):
        if isinstance(key, tuple):
            key = tuple(x.lower() if isinstance(x, str) else x for x in key)
        else:
            key = key.lower()

        return super().__getitem__(key)

    def get(self, key, default=None):
        if isinstance(key, tuple):
            key = tuple(x.lower() if isinstance(x, str) else x for x in key)
        else:
            key = key.lower()

        return super().get(key, default)

    def __setitem__(self, key, v):
        if isinstance(key, tuple):
            key = tuple(x.lower() if isinstance(x, str) else x for x in key)
        else:
            key = key.lower()

        super().__setitem__(key, v)







def _get_maybe_first(dict_items, lookup, default=None):
    try:
        items = dict_items[lookup]
    except KeyError:
        return default
    else:
        try:
            return items[0]
        except (IndexError, KeyError):
            return default
