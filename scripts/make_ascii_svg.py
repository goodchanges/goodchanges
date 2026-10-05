from pathlib import Path
from html import escape

from PIL import Image


INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

RAMP = " .`:-=+*cs#%@"

COLS = 90

FONT_SIZE = 7
CHAR_WIDTH = 4.2
ROW_HEIGHT = 8.5

TEXT_COLOR = "#c9d1d9"


def brightness_to_char(value):
    index = int((value / 255) * (len(RAMP) - 1))
    return RAMP[index]


def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"{INPUT} not found."
        )

    image = Image.open(INPUT).convert("L")

    original_width, original_height = image.size

    # Keep the portrait proportions.
    rows = int(
        (original_height / original_width)
        * COLS
        * 0.48
    )

    image = image.resize(
        (COLS, rows)
    )

    pixels = image.load()

    lines = []

    for y in range(rows):

        line = ""

        for x in range(COLS):

            brightness = pixels[x, y]

            char = brightness_to_char(
                brightness
            )

            line += char

        lines.append(line)

    width = COLS * CHAR_WIDTH
    height = rows * ROW_HEIGHT + 20

    svg = []

    svg.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{width}"
        height="{height}"
        viewBox="0 0 {width} {height}"
        xml:space="preserve">'''
    )

    # Background.
    svg.append(
        f'''
        <rect
            width="{width}"
            height="{height}"
            fill="#0d1117"/>
        '''
    )

    # Main ASCII text.
    svg.append(
        f'''
        <g
            font-family="Consolas, 'Courier New', monospace"
            font-size="{FONT_SIZE}px"
            fill="{TEXT_COLOR}"
            xml:space="preserve">
        '''
    )

    for row, line in enumerate(lines):

        y = 12 + row * ROW_HEIGHT

        delay = row * 0.035

        # One clip for each row.
        clip_id = f"clip_{row}"

        svg.append(
            f'''
            <clipPath id="{clip_id}">
                <rect
                    x="0"
                    y="{y - ROW_HEIGHT}"
                    width="0"
                    height="{ROW_HEIGHT + 2}">
                    <animate
                        attributeName="width"
                        from="0"
                        to="{width}"
                        begin="{delay:.2f}s"
                        dur="0.7s"
                        fill="freeze"/>
                </rect>
            </clipPath>
            '''
        )

        svg.append(
            f'''
            <text
                x="2"
                y="{y}"
                clip-path="url(#{clip_id})">
                {escape(line)}
            </text>
            '''
        )

    svg.append("</g>")

    # Cursor effect.
    total_time = rows * 0.035 + 0.7

    svg.append(
        f'''
        <rect
            x="0"
            y="0"
            width="3"
            height="{height}"
            fill="{TEXT_COLOR}"
            opacity="0">
            <animate
                attributeName="opacity"
                values="0;1;1;0"
                begin="0s"
                dur="{total_time:.2f}s"
                fill="freeze"/>
        </rect>
        '''
    )

    svg.append("</svg>")

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print(
        f"Created {OUTPUT}"
    )

    print(
        f"Grid: {COLS} columns x {rows} rows"
    )


if __name__ == "__main__":
    main()