#!/usr/bin/env python3
"""Build the registered source-art proof for the remaining stall attachments."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "art/source-assets/home-menu/stall/v004-attachment-kit"
BASE = ROOT / "docs/checkpoints/assets/home-menu-v009-approved-stall-lanterns.png"
REGISTERED = PACK / "registered/stall-attachment-full-context-candidate-v001.png"
BOARD = PACK / "reviews/stall-attachment-full-context-approval-board-v001.png"

CANVAS = (720, 1280)
STAGE_SCALE = 0.86
STAGE_PIVOT = (360.0, 634.0)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"),
        Path("/System/Library/Fonts/Avenir Next Condensed.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def load(relative: str) -> Image.Image:
    return Image.open(PACK / relative).convert("RGBA")


def stage_box(box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    x, y, width, height = box
    mapped_x = STAGE_PIVOT[0] + (x - STAGE_PIVOT[0]) * STAGE_SCALE
    mapped_y = STAGE_PIVOT[1] + (y - STAGE_PIVOT[1]) * STAGE_SCALE
    return (
        round(mapped_x),
        round(mapped_y),
        max(1, round(width * STAGE_SCALE)),
        max(1, round(height * STAGE_SCALE)),
    )


def exact(asset: Image.Image, width: int, height: int) -> Image.Image:
    return asset.resize((max(1, width), max(1, height)), Image.Resampling.LANCZOS)


def fit(asset: Image.Image, width: int, height: int) -> Image.Image:
    scale = min(width / asset.width, height / asset.height)
    return asset.resize(
        (max(1, round(asset.width * scale)), max(1, round(asset.height * scale))),
        Image.Resampling.LANCZOS,
    )


def place_exact(canvas: Image.Image, asset: Image.Image, logical_box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    x, y, width, height = stage_box(logical_box)
    canvas.alpha_composite(exact(asset, width, height), (x, y))
    return (x, y, width, height)


def place_fit_bottom(canvas: Image.Image, asset: Image.Image, logical_box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    x, y, width, height = stage_box(logical_box)
    fitted = fit(asset, width, height)
    left = x + (width - fitted.width) // 2
    top = y + height - fitted.height
    canvas.alpha_composite(fitted, (left, top))
    return (left, top, fitted.width, fitted.height)


def horizontal_nine_slice(asset: Image.Image, width: int, height: int, source_caps: tuple[int, int]) -> Image.Image:
    # First scale uniformly to the target height so corners and borders keep
    # their authored weight, then stretch only the clean horizontal center.
    scale = height / asset.height
    scaled_width = max(1, round(asset.width * scale))
    scaled = asset.resize((scaled_width, height), Image.Resampling.LANCZOS)
    left_cap = max(1, round(source_caps[0] * scale))
    right_cap = max(1, round(source_caps[1] * scale))
    if left_cap + right_cap >= width or left_cap + right_cap >= scaled.width:
        return exact(asset, width, height)

    output = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    left = scaled.crop((0, 0, left_cap, height))
    center = scaled.crop((left_cap, 0, scaled.width - right_cap, height))
    right = scaled.crop((scaled.width - right_cap, 0, scaled.width, height))
    output.alpha_composite(left, (0, 0))
    output.alpha_composite(center.resize((width - left_cap - right_cap, height), Image.Resampling.LANCZOS), (left_cap, 0))
    output.alpha_composite(right, (width - right_cap, 0))
    return output


def place_nine_slice(canvas: Image.Image, asset: Image.Image, logical_box: tuple[float, float, float, float], source_caps: tuple[int, int]) -> tuple[int, int, int, int]:
    x, y, width, height = stage_box(logical_box)
    canvas.alpha_composite(horizontal_nine_slice(asset, width, height, source_caps), (x, y))
    return (x, y, width, height)


def draw_button_label(canvas: Image.Image, mapped_box: tuple[int, int, int, int], text: str, size: int) -> None:
    x, y, width, height = mapped_box
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    label_font = font(size, True)
    bounds = draw.textbbox((0, 0), text, font=label_font, stroke_width=1)
    text_width = bounds[2] - bounds[0]
    text_height = bounds[3] - bounds[1]
    tx = x + (width - text_width) / 2
    ty = y + (height - text_height) / 2 - bounds[1] - 1
    draw.text((tx + 1, ty + 2), text, font=label_font, fill=(38, 22, 12, 220), stroke_width=2, stroke_fill=(38, 22, 12, 150))
    draw.text((tx, ty), text, font=label_font, fill=(245, 220, 164, 255), stroke_width=1, stroke_fill=(92, 52, 24, 255))
    canvas.alpha_composite(layer)


def draw_leaf_pair(canvas: Image.Image, mapped_box: tuple[int, int, int, int]) -> None:
    x, y, width, height = mapped_box
    left = load("ui/components/buttons/menu-button-leaf-left-v001.png")
    right = load("ui/components/buttons/menu-button-leaf-right-v001.png")
    leaf_h = max(9, round(height * 0.32))
    left_fit = fit(left, round(width * 0.11), leaf_h)
    right_fit = fit(right, round(width * 0.11), leaf_h)
    canvas.alpha_composite(left_fit, (x + round(width * 0.045), y + (height - left_fit.height) // 2))
    canvas.alpha_composite(right_fit, (x + width - right_fit.width - round(width * 0.045), y + (height - right_fit.height) // 2))


def make_registered() -> Image.Image:
    base = Image.open(BASE).convert("RGBA").resize(CANVAS, Image.Resampling.LANCZOS)

    # UI faces first, so the cloth can naturally overlap the first button.
    plaque = load("ui/components/rank/rank-plaque-empty-sockets-v001.png")
    plaque_box = place_nine_slice(base, plaque, (246, 372, 228, 48), (185, 185))
    filled_star = load("ui/components/rank/rank-star-filled-v001.png")
    for star_box in ((279, 381, 42, 34), (339, 381, 42, 34), (399, 381, 42, 34)):
        place_exact(base, filled_star, star_box)

    primary = load("ui/components/buttons/menu-button-primary-normal-v001.png")
    secondary = load("ui/components/buttons/menu-button-secondary-normal-v001.png")
    menu = [
        (primary, (222, 770, 292, 72), "Open Stall", 27),
        (secondary, (223, 852, 290, 64), "Guestbook", 24),
        (secondary, (223, 926, 290, 64), "Decorations", 22),
        (secondary, (223, 1000, 290, 64), "Pantry", 24),
    ]
    for asset, box, label, size in menu:
        mapped = place_nine_slice(base, asset, box, (72, 72))
        draw_leaf_pair(base, mapped)
        draw_button_label(base, mapped, label, size)

    settings = load("ui/components/settings/settings-cog-normal-v001.png")
    place_fit_bottom(base, settings, (515, 1033, 75, 84))

    # Counter contact shadows.
    place_exact(base, load("stockpot/components/stall_stockpot_contact_shadow_candidate_v001.png"), (132, 709, 94, 18))
    place_exact(base, load("counter-small/cutouts/counter-oil-lantern-contact-shadow-candidate-v001.png"), (205, 704, 72, 18))

    # Plant behind the crate and cloth. Components remain independently animatable.
    place_exact(base, load("counter-decor/components/counter_plant_foliage_candidate_v001.png"), (486, 500, 61, 154))
    place_exact(base, load("counter-decor/components/counter_plant_pot_candidate_v001.png"), (481, 644, 67, 75))

    # Pot: exact concept registration deliberately shows the separate body/lid relationship.
    place_exact(base, load("stockpot/components/stall_stockpot_body_open_candidate_v001.png"), (136, 626, 86, 92))
    place_exact(base, load("stockpot/components/stall_stockpot_lid_candidate_v001.png"), (133, 589, 90, 49))

    place_exact(base, load("counter-small/cutouts/grape-food-bowl-candidate-v001.png"), (157, 652, 66, 66))

    # Counter lantern ON composition: shadow + halo + unchanged shell + core.
    halo = load("counter-small/cutouts/counter-oil-lantern-halo-add-candidate-v001.png")
    halo_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    place_fit_bottom(halo_layer, halo, (186, 581, 110, 146))
    halo_layer.putalpha(halo_layer.getchannel("A").point(lambda value: round(value * 0.55)))
    base.alpha_composite(halo_layer)
    place_exact(base, load("counter-small/cutouts/counter-oil-lantern-body-off-candidate-v001.png"), (209, 604, 63, 115))
    place_fit_bottom(base, load("counter-small/cutouts/counter-oil-lantern-core-add-candidate-v001.png"), (225, 646, 31, 58))

    place_exact(base, load("counter-decor/components/bottle_crate_assembled_preview_candidate_v001.png"), (470, 618, 117, 101))
    place_exact(base, load("counter-decor/components/counter_cloth_red_draped_candidate_v001.png"), (517, 684, 97, 120))

    # A restrained procedural-steam mock appears only in this review composite.
    steam = Image.new("RGBA", base.size, (0, 0, 0, 0))
    steam_draw = ImageDraw.Draw(steam)
    x, y, _, _ = stage_box((170, 555, 55, 78))
    steam_draw.arc((x, y + 22, x + 28, y + 66), 95, 270, fill=(220, 224, 218, 105), width=5)
    steam_draw.arc((x + 12, y, x + 42, y + 49), 265, 95, fill=(220, 224, 218, 82), width=4)
    steam = steam.filter(ImageFilter.GaussianBlur(1.0))
    base.alpha_composite(steam)

    return base


def make_board(registered: Image.Image) -> Image.Image:
    board = Image.new("RGBA", (1600, 1500), "#17202B")
    draw = ImageDraw.Draw(board)
    title = "VISUAL GATE 03 — COMPLETE STALL ATTACHMENT KIT"
    title_font = font(42, True)
    bounds = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((1600 - (bounds[2] - bounds[0])) // 2, 24), title, font=title_font, fill="#F4E9CF")
    subtitle = "registered against approved V009 stall — main character intentionally excluded"
    subtitle_font = font(23)
    bounds = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    draw.text(((1600 - (bounds[2] - bounds[0])) // 2, 79), subtitle, font=subtitle_font, fill="#B8C0CD")

    preview = registered.resize((720, 1280), Image.Resampling.LANCZOS)
    board.alpha_composite(preview, (56, 136))

    panel = (824, 136, 1544, 1416)
    draw.rounded_rectangle(panel, radius=24, fill="#253241")
    sections = [
        ("COUNTER", ["separate stockpot body + lid", "procedural steam preview", "counter lantern OFF shell + ON core/halo", "green food bowl"]),
        ("DECOR", ["plant pot + foliage", "crate + 3 independent bottles", "assembled bottle prefab", "draped red cloth"]),
        ("STALL UI", ["rank plaque + 3 star states", "primary + secondary button systems", "normal / selected / pressed / disabled", "native labels + detached leaves", "settings normal + pressed"]),
        ("NOT IN THIS GATE", ["main Bentosaur character", "warm spill from hanging lanterns", "final runtime animation tuning"]),
    ]
    cursor_y = 180
    for heading, lines in sections:
        draw.text((870, cursor_y), heading, font=font(26, True), fill="#F4E9CF")
        cursor_y += 45
        for line in lines:
            draw.ellipse((876, cursor_y + 10, 886, cursor_y + 20), fill="#D5A95B")
            draw.text((905, cursor_y), line, font=font(22), fill="#C7CED8")
            cursor_y += 39
        cursor_y += 26

    draw.rounded_rectangle((858, 1180, 1510, 1368), radius=16, fill="#1D2834")
    draw.text((888, 1210), "FOUNDER DECISION", font=font(25, True), fill="#F4E9CF")
    draw.text((888, 1254), "Approve or revise per category.", font=font(22), fill="#C7CED8")
    draw.text((888, 1292), "Nothing here is in the game yet.", font=font(22), fill="#D5A95B")
    draw.text((888, 1330), "Brown plaque face is still flagged.", font=font(20), fill="#D5A95B")
    return board


def main() -> None:
    REGISTERED.parent.mkdir(parents=True, exist_ok=True)
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    registered = make_registered()
    registered.convert("RGB").save(REGISTERED, quality=95)
    make_board(registered).convert("RGB").save(BOARD, quality=95)
    print(REGISTERED)
    print(BOARD)


if __name__ == "__main__":
    main()
