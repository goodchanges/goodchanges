from pathlib import Path
import os


OUTPUT = Path("info-card.svg")

STATIC = os.getenv("STATIC") == "1"

WIDTH = 490
HEIGHT = 340


ROWS = [
    ("Name", "Ayush Kumar Verma"),
    ("Role", "CSE Student"),
    ("Focus", "AI / Backend / Open Source"),
    ("Languages", "C++ / Python / Java"),
    ("Open Source", "Kestra / LiteLLM / Neo4j"),
    ("Building", "AI + Developer Tools"),
]


def main():
    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}">'
    )

    svg.append("""
    <rect
        width="490"
        height="340"
        rx="14"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="2"/>
    """)

    # Terminal title bar.
    svg.append("""
    <circle cx="20" cy="20" r="5" fill="#ff5f56"/>
    <circle cx="38" cy="20" r="5" fill="#ffbd2e"/>
    <circle cx="56" cy="20" r="5" fill="#27c93f"/>
    """)

    svg.append("""
    <text
        x="80"
        y="26"
        fill="#8b949e"
        font-family="monospace"
        font-size="14">
        goodchanges@github
    </text>
    """)

    # Separator.
    svg.append("""
    <line
        x1="20"
        y1="48"
        x2="470"
        y2="48"
        stroke="#30363d"/>
    """)

    y = 82

    for index, (key, value) in enumerate(ROWS):

        delay = 0.25 + index * 0.18

        if STATIC:
            animation = ""
        else:
            animation = f"""
            <animate
                attributeName="opacity"
                from="0"
                to="1"
                begin="{delay:.2f}s"
                dur="0.35s"
                fill="freeze"/>
            """

        svg.append(f"""
        <g opacity="0">
            <text
                x="22"
                y="{y}"
                fill="#8b949e"
                font-family="monospace"
                font-size="15">
                {key}
            </text>

            <text
                x="145"
                y="{y}"
                fill="#f0f6fc"
                font-family="monospace"
                font-size="15">
                {value}
            </text>

            {animation}
        </g>
        """)

        y += 40

    svg.append("""
    <text
        x="22"
        y="325"
        fill="#58a6ff"
        font-family="monospace"
        font-size="13">
        $ open_source --status
    </text>
    """)

    svg.append("</svg>")

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()