"""Build a labeled contact sheet for the facial proof renders."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ITEMS = (
    ("01_neutral_face.png", "NEUTRAL / CLOSE CORRECTIVE"),
    ("02_partial_face.png", "50% MOUTH MORPH"),
    ("03_open_face.png", "DELIGHTED OPEN + JAW + TONGUE"),
    ("04_blink_face.png", "INDEPENDENT BLINK TARGETS"),
    ("05_happy_face.png", "HAPPY EYES + OPEN"),
    ("06_chew_face.png", "CHEW COMPRESS + TONGUE"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    renders = root / "evidence" / "renders"
    target = root / "evidence" / "facial_states_contact_sheet.png"
    images = [Image.open(renders / filename).convert("RGB") for filename, _ in ITEMS]
    thumb = 520
    header = 72
    gap = 14
    columns = 3
    rows = 2
    canvas = Image.new(
        "RGB",
        (
            columns * thumb + (columns + 1) * gap,
            rows * (thumb + header) + (rows + 1) * gap,
        ),
        (14, 20, 26),
    )
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=22)
    for index, (image, (_filename, label)) in enumerate(zip(images, ITEMS, strict=True)):
        row, column = divmod(index, columns)
        x = gap + column * (thumb + gap)
        y = gap + row * (thumb + header + gap)
        resized = image.resize((thumb, thumb), Image.Resampling.LANCZOS)
        canvas.paste(resized, (x, y))
        draw.rounded_rectangle(
            (x, y + thumb, x + thumb, y + thumb + header),
            radius=8,
            fill=(28, 40, 49),
        )
        draw.text(
            (x + 16, y + thumb + 24),
            label,
            fill=(238, 226, 203),
            font=font,
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, quality=95)
    print(target)


if __name__ == "__main__":
    main()
