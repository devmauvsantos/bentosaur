#!/usr/bin/env python3
"""Build the founder-facing stockpot candidate board for Visual Gate 03."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "art/source-assets/home-menu/stall/v004-attachment-kit/stockpot"
COMPONENTS = PACK / "components"
OUTPUT = PACK / "reviews/stockpot-category-review-board-v001.png"

BG = "#17202B"
PANEL = "#253241"
CREAM = "#F4E9CF"
MUTED = "#B8C0CD"
AMBER = "#D5A95B"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/SFNS.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def fit(asset: Image.Image, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / asset.width, max_height / asset.height)
    return asset.resize(
        (max(1, round(asset.width * scale)), max(1, round(asset.height * scale))),
        Image.Resampling.LANCZOS,
    )


def center_asset(board: Image.Image, asset: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    fitted = fit(asset, x1 - x0, y1 - y0)
    x = x0 + ((x1 - x0) - fitted.width) // 2
    y = y0 + ((y1 - y0) - fitted.height) // 2
    board.alpha_composite(fitted, (x, y))


def centered_text(draw: ImageDraw.ImageDraw, text: str, y: int, text_font: ImageFont.ImageFont, fill: str) -> None:
    bounds = draw.textbbox((0, 0), text, font=text_font)
    draw.text(((1600 - (bounds[2] - bounds[0])) // 2, y), text, font=text_font, fill=fill)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    board = Image.new("RGBA", (1600, 1080), BG)
    draw = ImageDraw.Draw(board)

    centered_text(draw, "VISUAL GATE 03 — MODULAR STOCKPOT", 24, font(48, True), CREAM)
    centered_text(draw, "complete open body · separate pivotable lid · procedural steam later", 84, font(24), MUTED)

    cards = [(42, 150, 510, 845), (566, 150, 1034, 845), (1090, 150, 1558, 845)]
    for card in cards:
        draw.rounded_rectangle(card, radius=20, fill=PANEL)

    labels = ["OPEN BODY", "SEPARATE LID", "CLOSED PREVIEW"]
    for label, card in zip(labels, cards):
        label_font = font(30, True)
        bounds = draw.textbbox((0, 0), label, font=label_font)
        x = card[0] + ((card[2] - card[0]) - (bounds[2] - bounds[0])) // 2
        draw.text((x, card[1] + 22), label, font=label_font, fill=CREAM)

    body = Image.open(COMPONENTS / "stall_stockpot_body_open_candidate_v001.png").convert("RGBA")
    lid = Image.open(COMPONENTS / "stall_stockpot_lid_candidate_v001.png").convert("RGBA")
    preview = Image.open(COMPONENTS / "stall_stockpot_assembled_preview_candidate_v001.png").convert("RGBA")
    shadow = Image.open(COMPONENTS / "stall_stockpot_contact_shadow_candidate_v001.png").convert("RGBA")

    center_asset(board, body, (75, 255, 477, 695))
    center_asset(board, lid, (600, 270, 1000, 605))
    center_asset(board, preview, (1120, 230, 1528, 700))
    center_asset(board, shadow, (1120, 690, 1528, 765))

    pivot_y = 650
    draw.line((665, pivot_y, 935, pivot_y), fill=AMBER, width=3)
    draw.ellipse((793, pivot_y - 7, 807, pivot_y + 7), fill=AMBER)
    draw.text((665, pivot_y + 16), "planned bottom-center sprite pivot", font=font(20), fill=MUTED)

    draw.rounded_rectangle((42, 885, 1558, 1028), radius=18, fill="#202C39")
    draw.text((72, 910), "RUNTIME CONTRACT", font=font(24, True), fill=CREAM)
    draw.text((72, 952), "Lid: restrained occasional rattle  •  Steam: Godot effect, not baked art  •  Body remains complete while lid lifts", font=font(23), fill=MUTED)
    draw.text((72, 997), "Candidate source only — final counter scale and registration require founder approval", font=font(20), fill=AMBER)

    board.convert("RGB").save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
