import urllib.parse
import urllib.request
from typing import Any

import orjson


MOCK_API_BASE_URL = "https://api.clashapi.dev"


def load_mock_api(endpoint: str) -> dict[str, Any]:
    url = urllib.parse.urljoin(MOCK_API_BASE_URL, endpoint)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "clashy.py tests"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return orjson.loads(response.read())

