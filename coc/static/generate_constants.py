from pathlib import Path
import json

with open("static_data.json", "r", encoding="utf-8") as f:
    static_data: dict = json.load(f)

troops = static_data["troops"]
spells = static_data["spells"]
heroes = static_data["heroes"]
equipment = static_data["equipment"]
pets = static_data["pets"]
buildings = static_data["buildings"]
achievements = static_data["achievements"]

lists_to_write = {
    'ELIXIR_TROOP_ORDER':  [
        t["name"] for t in troops
        if t["production_building"] == "Barracks"
           and not t.get("is_seasonal", False)
           and not "super_troop" in t
    ],
    'DARK_ELIXIR_TROOP_ORDER': [
        t["name"] for t in troops
        if t["production_building"] == "Dark Barracks"
           and not t.get("is_seasonal", False)
           and not "super_troop" in t
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
        a["name"] for a in sorted(achievements,
                                  key=lambda x: ({'home': 0, 'builderBase': 1, 'clanCapital': 2}.get(
                                      x["village"], 0), -x["ui_priority"]))
    ], # same order as in-game
}
constants_path = Path(__file__).parent.parent / "constants.py"

with open(constants_path, 'w') as f:
    f.write('"""Auto-generated constants from static game data."""\n\n')
    for name, lst in lists_to_write.items():
        if isinstance(lst, str):
            f.write(f"{name} = {lst}\n\n")
        else:
            # Manual formatting: each item on its own line
            f.write(f"{name} = [\n")
            for item in lst:
                f.write(f"    {repr(item)},\n")
            f.write("]\n\n")

print(f"Constants written to {constants_path}")