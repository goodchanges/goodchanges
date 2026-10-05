import json
from datetime import date, timedelta
from pathlib import Path


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")


WIDTH = 860
CELL = 11
GAP = 3
STEP = CELL + GAP

LEFT = 42
TOP = 30

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]


def sunday_index(d):
    # Python Monday=0 ... Sunday=6
    return (d.weekday() + 1) % 7


def main():

    data = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    days = data["days"]

    lookup = {
        date.fromisoformat(day["date"]): day
        for day in days
    }

    dates = sorted(lookup)

    first = dates[0]
    last = dates[-1]

    grid_start = first - timedelta(
        days=sunday_index(first)
    )

    grid_end = last + timedelta(
        days=6 - sunday_index(last)
    )

    columns = (
        (grid_end - grid_start).days // 7
    ) + 1

    grid_width = LEFT + columns * STEP + 20

    height = 155

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {grid_width} {height}" '
        f'width="{WIDTH}" height="{height}">'
    )

    svg.append("""
    <rect
        width="100%"
        height="100%"
        rx="14"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="1"/>
    """)

    # Heading.
    svg.append("""
    <text
        x="18"
        y="17"
        fill="#8b949e"
        font-family="monospace"
        font-size="11">
        contribution activity
    </text>
    """)

    # Weekday labels.
    labels = [
        ("Mon", 1),
        ("Wed", 3),
        ("Fri", 5),
    ]

    for label, row in labels:

        y = TOP + row * STEP + 9

        svg.append(
            f'<text x="5" y="{y}" '
            f'fill="#8b949e" '
            f'font-family="monospace" '
            f'font-size="8">{label}</text>'
        )

    # Month labels.
    seen_months = set()

    for col in range(columns):

        column_date = (
            grid_start
            + timedelta(days=col * 7)
        )

        month_key = (
            column_date.year,
            column_date.month
        )

        if month_key in seen_months:
            continue

        seen_months.add(month_key)

        month_name = column_date.strftime("%b")

        x = LEFT + col * STEP

        svg.append(
            f'<text x="{x}" y="27" '
            f'fill="#8b949e" '
            f'font-family="monospace" '
            f'font-size="9">{month_name}</text>'
        )

    # Contribution cells.
    for d in dates:

        delta = (
            d - grid_start
        ).days

        col = delta // 7
        row = delta % 7

        level = lookup[d]["level"]

        level = max(
            0,
            min(level, len(PALETTE) - 1)
        )

        x = LEFT + col * STEP
        y = TOP + row * STEP

        delay = (
            0.15
            + (col + row) * 0.035
        )

        color = PALETTE[level]

        svg.append(f"""
        <rect
            x="{x}"
            y="{y}"
            width="{CELL}"
            height="{CELL}"
            rx="3"
            fill="{color}"
            opacity="0">

            <animate
                attributeName="opacity"
                from="0"
                to="1"
                begin="{delay:.2f}s"
                dur="0.30s"
                fill="freeze"/>

            <animateTransform
                attributeName="transform"
                type="translate"
                from="0 -8"
                to="0 0"
                begin="{delay:.2f}s"
                dur="0.30s"
                fill="freeze"/>
        </rect>
        """)

    # Legend.
    legend_y = TOP + 7 * STEP + 9

    svg.append("""
    <text
        x="18"
        y="145"
        fill="#8b949e"
        font-family="monospace"
        font-size="9">
        Less
    </text>
    """)

    for level in range(5):

        x = 55 + level * 18

        svg.append(
            f'<rect x="{x}" y="136" '
            f'width="11" height="11" rx="3" '
            f'fill="{PALETTE[level]}"/>'
        )

    svg.append("""
    <text
        x="155"
        y="145"
        fill="#8b949e"
        font-family="monospace"
        font-size="9">
        More
    </text>
    """)

    # Statistics.
    total = data.get(
        "total_contributions"
    )

    current = data.get(
        "current_streak",
        0
    )

    longest = data.get(
        "longest_streak",
        0
    )

    if total is None:
        total_text = "Contribution data tracked"
    else:
        total_text = f"{total:,} contributions"

    stats = (
        f"{total_text}  •  "
        f"current streak: {current}  •  "
        f"best streak: {longest}"
    )

    svg.append(
        f'<text x="340" y="145" '
        f'fill="#8b949e" '
        f'font-family="monospace" '
        f'font-size="9">{stats}</text>'
    )

    svg.append("</svg>")

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()