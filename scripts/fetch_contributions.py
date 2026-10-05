import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "goodchanges"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT = Path("data/contributions.json")


def parse_count(text):
    match = re.search(
        r"(\d[\d,]*)\s+contributions?",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    return int(match.group(1).replace(",", ""))


def calculate_streaks(days):
    counts = {
        date.fromisoformat(day["date"]): (day["count"] or 0)
        for day in days
    }

    if not counts:
        return 0, 0

    all_dates = sorted(counts)

    current = 0

    d = all_dates[-1]

    while d in counts and counts[d] > 0:
        current += 1
        d -= timedelta(days=1)

    longest = 0
    running = 0

    start = all_dates[0]
    end = all_dates[-1]

    d = start

    while d <= end:

        if counts.get(d, 0) > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

        d += timedelta(days=1)

    return current, longest


def calculate_months(days):
    totals = defaultdict(int)

    for day in days:

        if day["count"] is None:
            continue

        dt = date.fromisoformat(day["date"])

        key = dt.strftime("%Y-%m")

        totals[key] += day["count"]

    return [
        {
            "month": month,
            "count": count
        }
        for month, count in sorted(totals.items())
    ]


def main():

    print(f"Fetching {URL}")

    response = requests.get(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "GitHubContributionProfile/1.0"
            )
        },
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    cells = soup.select(
        ".js-calendar-graph-table "
        ".ContributionCalendar-day[data-date][data-level]"
    )

    if not cells:
        cells = soup.select(
            ".ContributionCalendar-day[data-date][data-level]"
        )

    if not cells:
        raise RuntimeError(
            "Could not find contribution cells. "
            "GitHub may have changed its HTML structure."
        )

    tooltips = {}

    for tooltip in soup.select("tool-tip[for]"):
        key = tooltip.get("for")

        if key:
            tooltips[key] = tooltip.get_text(
                " ",
                strip=True
            )

    days = []

    for cell in cells:

        raw_date = cell.get("data-date")
        raw_level = cell.get("data-level")

        if not raw_date or raw_level is None:
            continue

        level = int(raw_level)

        cell_id = cell.get("id")

        count = None

        if cell_id and cell_id in tooltips:
            count = parse_count(
                tooltips[cell_id]
            )

        # Level 0 always means zero contributions.
        if level == 0 and count is None:
            count = 0

        days.append(
            {
                "date": raw_date,
                "level": level,
                "count": count,
            }
        )

    days.sort(
        key=lambda item: item["date"]
    )

    if not days:
        raise RuntimeError(
            "No contribution days were parsed."
        )

    current_streak, longest_streak = calculate_streaks(
        days
    )

    known_counts = [
        day["count"]
        for day in days
        if day["count"] is not None
    ]

    total = (
        sum(known_counts)
        if len(known_counts) == len(days)
        else None
    )

    best_day = None

    known_days = [
        day for day in days
        if day["count"] is not None
    ]

    if known_days:
        best_day = max(
            known_days,
            key=lambda day: day["count"]
        )

    output = {
        "username": USERNAME,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "total_contributions": total,

        "current_streak": current_streak,

        "longest_streak": longest_streak,

        "best_day": best_day,

        "monthly_totals": calculate_months(
            days
        ),

        "days": days,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"Parsed {len(days)} contribution days."
    )

    print(
        f"Total: {total}"
    )

    print(
        f"Current streak: {current_streak}"
    )

    print(
        f"Longest streak: {longest_streak}"
    )

    print(
        f"Saved to {OUTPUT}"
    )


if __name__ == "__main__":
    main()