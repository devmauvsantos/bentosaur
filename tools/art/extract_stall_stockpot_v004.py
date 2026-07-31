#!/usr/bin/env python3
"""Extract deterministic stockpot components from the immutable V004 sheet."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "art/source-assets/home-menu/stall/v004-attachment-kit/stockpot"
SOURCE = PACK / "generated/stockpot-modular-sheet-cutout-candidate-v001.png"
OUT = PACK / "components"


def crop_band(image: Image.Image, y0: int, y1: int, filename: str) -> dict[str, object]:
    band = image.crop((0, y0, image.width, y1))
    alpha = band.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError(f"No visible pixels found for {filename}")

    pad = 8
    left = max(0, bbox[0] - pad)
    top = max(0, bbox[1] - pad)
    right = min(band.width, bbox[2] + pad)
    bottom = min(band.height, bbox[3] + pad)
    component = band.crop((left, top, right, bottom))
    destination = OUT / filename
    component.save(destination)

    return {
        "file": str(destination.relative_to(ROOT)),
        "source_box": [left, y0 + top, right, y0 + bottom],
        "size": list(component.size),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE).convert("RGBA")

    components = [
        crop_band(image, 0, 585, "stall_stockpot_body_open_candidate_v001.png"),
        crop_band(image, 585, 955, "stall_stockpot_lid_candidate_v001.png"),
        crop_band(image, 955, 1175, "stall_stockpot_contact_shadow_candidate_v001.png"),
        crop_band(image, 1175, image.height, "stall_stockpot_assembled_preview_candidate_v001.png"),
    ]

    print("Extracted stockpot components:")
    for component in components:
        print(f"- {component['file']} {component['size']} from {component['source_box']}")


if __name__ == "__main__":
    main()
