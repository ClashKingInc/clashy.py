"""Print typed variants from an in-game account export (no API requests).

Usage: python examples/townhall_variants.py /path/to/account-export.json
"""
import asyncio
import json
import sys
from pathlib import Path

import coc


async def main():
    export = json.loads(Path(sys.argv[1]).read_text())
    async with coc.Client() as client:
        # Supplied tokens initialize the bundled catalog without a network request.
        await client.login_with_tokens("offline-account-export")
        account = client.parse_account_data(export)
        if account.townhall is None:
            print("This export does not include a home Town Hall")
            return
        for variant in account.townhall.variants:
            print(variant.name, "owned:", variant.is_owned)
            if variant.required_troop is not None:
                print("Requires", variant.required_troop.name, "level", variant.required_troop_level)


if __name__ == "__main__":
    asyncio.run(main())
