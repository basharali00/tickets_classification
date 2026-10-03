"""Load sample_tickets.json through POST /tickets.

Run: docker compose exec api python load_sample_tickets.py
Safe to re-run: existing tickets return 409 and are skipped.
"""

import json
import urllib.error
import urllib.request

from packages.settings import settings


def main() -> None:
    with open("sample_tickets.json", encoding="utf-8") as f:
        tickets = json.load(f)

    for ticket in tickets:
        request = urllib.request.Request(
            f"{settings.BASE_URL}/tickets",
            data=json.dumps(ticket).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request) as response:
                print(f"{ticket['id']}: {response.status} created")
        except urllib.error.HTTPError as e:
            print(f"{ticket['id']}: {e.code} {e.read().decode()}")


if __name__ == "__main__":
    main()
