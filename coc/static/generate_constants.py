from pathlib import Path
from urllib.request import Request, urlopen
import json


STATIC_DATA_URL = "https://assets.clashk.ing/static_data.json"
TRANSLATIONS_URL = "https://assets.clashk.ing/translations.json"
STATIC_DIR = Path(__file__).parent
STATIC_DATA_PATH = STATIC_DIR / "static_data.json"
TRANSLATIONS_PATH = STATIC_DIR / "translations.json"
CONSTANTS_PATH = STATIC_DIR.parent / "constants.py"


def download_json(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "clashy.py constants generator"})
    with urlopen(request, timeout=30) as response:
        data = response.read()
    json.loads(data)
    return data


def update_static_files(
    static_data_url: str = STATIC_DATA_URL,
    translations_url: str = TRANSLATIONS_URL,
    static_data_path: Path = STATIC_DATA_PATH,
    translations_path: Path = TRANSLATIONS_PATH,
) -> None:
    static_data = download_json(static_data_url)
    translations = download_json(translations_url)
    static_data_path.write_bytes(static_data)
    translations_path.write_bytes(translations)


def build_constants(static_data: dict) -> dict:
    troops = static_data["troops"]
    spells = static_data["spells"]
    heroes = static_data["heroes"]
    equipment = static_data["equipment"]
    pets = static_data["pets"]
    buildings = static_data["buildings"]
    achievements = static_data["achievements"]

    return {
        'ELIXIR_TROOP_ORDER': [
            t["name"] for t in troops
            if t["production_building"] == "Barracks"
               and not t.get("is_seasonal", False)
               and "super_troop" not in t
        ],
        'DARK_ELIXIR_TROOP_ORDER': [
            t["name"] for t in troops
            if t["production_building"] == "Dark Barracks"
               and not t.get("is_seasonal", False)
               and "super_troop" not in t
        ],
        'HV_TROOP_ORDER': 'ELIXIR_TROOP_ORDER + DARK_ELIXIR_TROOP_ORDER',
        'SIEGE_MACHINE_ORDER': [t["name"] for t in troops if t["production_building"] == "Workshop"],
        'SUPER_TROOP_ORDER': [t["name"] for t in troops if "super_troop" in t],
        'HOME_TROOP_ORDER': 'HV_TROOP_ORDER + SIEGE_MACHINE_ORDER',
        'SEASONAL_TROOP_ORDER': [t["name"] for t in troops if t.get("is_seasonal", False)],
        'BUILDER_TROOPS_ORDER': [t["name"] for t in troops if t["village"] == "builderBase"],
        'ELIXIR_SPELL_ORDER': [
            s["name"] for s in spells
            if s["upgrade_resource"] == "Elixir"
               and not s.get("is_seasonal", False)
        ],
        'DARK_ELIXIR_SPELL_ORDER': [s["name"] for s in spells if s["upgrade_resource"] == "Dark Elixir"],
        'SEASONAL_SPELL_ORDER': [s["name"] for s in spells if s.get("is_seasonal", False)],
        'SPELL_ORDER': 'ELIXIR_SPELL_ORDER + DARK_ELIXIR_SPELL_ORDER',
        'HOME_BASE_HERO_ORDER': [
            h["name"] for h in sorted(heroes, key=lambda x: x["levels"][0]["required_townhall"])
            if h["village"] == "home"
        ],
        'BUILDER_BASE_HERO_ORDER': [h["name"] for h in heroes if h["village"] == "builderBase"],
        'HERO_ORDER': 'HOME_BASE_HERO_ORDER + BUILDER_BASE_HERO_ORDER',
        'PETS_ORDER': [p["name"] for p in pets],
        'EQUIPMENT': [e["name"] for e in equipment],
        'HV_BUILDINGS': [b["name"] for b in buildings if b["village"] == "home"],
        'ACHIEVEMENT_ORDER': [
            a["name"] for a in sorted(
                achievements,
                key=lambda x: ({'home': 0, 'builderBase': 1, 'clanCapital': 2}.get(x["village"], 0),
                               -x["ui_priority"])
            )
        ],
    }


def write_constants(lists_to_write: dict, constants_path: Path = CONSTANTS_PATH) -> None:
    with constants_path.open("w", encoding="utf-8") as f:
        f.write('"""Auto-generated constants from static game data."""\n\n')
        for name, lst in lists_to_write.items():
            if isinstance(lst, str):
                f.write(f"{name} = {lst}\n\n")
            else:
                f.write(f"{name} = [\n")
                for item in lst:
                    f.write(f"    {repr(item)},\n")
                f.write("]\n\n")


def main() -> None:
    update_static_files()
    with STATIC_DATA_PATH.open("r", encoding="utf-8") as f:
        static_data: dict = json.load(f)
    write_constants(build_constants(static_data))
    print(f"Constants written to {CONSTANTS_PATH}")


if __name__ == "__main__":
    main()
