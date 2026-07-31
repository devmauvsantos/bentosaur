#!/usr/bin/env python3
"""Validate and inventory Visual Gate 03 source candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "art/source-assets/home-menu/stall/v004-attachment-kit"
MANIFEST = PACK / "manifest.json"

EXPECTED = [
    "stockpot/components/stall_stockpot_body_open_candidate_v001.png",
    "stockpot/components/stall_stockpot_lid_candidate_v001.png",
    "stockpot/components/stall_stockpot_contact_shadow_candidate_v001.png",
    "counter-small/cutouts/counter-oil-lantern-body-off-candidate-v001.png",
    "counter-small/cutouts/counter-oil-lantern-core-add-candidate-v001.png",
    "counter-small/cutouts/counter-oil-lantern-halo-add-candidate-v001.png",
    "counter-small/cutouts/counter-oil-lantern-contact-shadow-candidate-v001.png",
    "counter-small/cutouts/grape-food-bowl-candidate-v001.png",
    "counter-decor/components/counter_plant_pot_candidate_v001.png",
    "counter-decor/components/counter_plant_foliage_candidate_v001.png",
    "counter-decor/components/bottle_crate_empty_candidate_v001.png",
    "counter-decor/components/bottle_brown_candidate_v001.png",
    "counter-decor/components/bottle_green_candidate_v001.png",
    "counter-decor/components/bottle_cream_blue_cap_candidate_v001.png",
    "counter-decor/components/counter_cloth_red_draped_candidate_v001.png",
    "ui/components/rank/rank-plaque-empty-sockets-v001.png",
    "ui/components/rank/rank-star-empty-v001.png",
    "ui/components/rank/rank-star-filled-v001.png",
    "ui/components/rank/rank-star-shine-v001.png",
    "ui/components/buttons/menu-button-primary-normal-v001.png",
    "ui/components/buttons/menu-button-primary-selected-v001.png",
    "ui/components/buttons/menu-button-primary-pressed-v001.png",
    "ui/components/buttons/menu-button-primary-disabled-v001.png",
    "ui/components/buttons/menu-button-secondary-normal-v001.png",
    "ui/components/buttons/menu-button-secondary-selected-v001.png",
    "ui/components/buttons/menu-button-secondary-pressed-v001.png",
    "ui/components/buttons/menu-button-secondary-disabled-v001.png",
    "ui/components/buttons/menu-button-leaf-left-v001.png",
    "ui/components/buttons/menu-button-leaf-right-v001.png",
    "ui/components/settings/settings-cog-normal-v001.png",
    "ui/components/settings/settings-cog-pressed-v001.png",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def qa_png(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGBA")
    pixels = image.load()
    corners = [
        pixels[0, 0][3],
        pixels[image.width - 1, 0][3],
        pixels[0, image.height - 1][3],
        pixels[image.width - 1, image.height - 1][3],
    ]
    magenta = 0
    partial = 0
    for red, green, blue, alpha in image.get_flattened_data():
        if 0 < alpha < 255:
            partial += 1
        if alpha > 0 and red > 170 and blue > 170 and green < 90:
            magenta += 1
    return {
        "size": [image.width, image.height],
        "corner_alpha": corners,
        "partial_alpha_pixels": partial,
        "magenta_fringe_pixels": magenta,
    }


def main() -> None:
    missing = [relative for relative in EXPECTED if not (PACK / relative).exists()]
    if missing:
        raise SystemExit("Missing expected components:\n- " + "\n- ".join(missing))

    component_qa: dict[str, object] = {}
    for relative in EXPECTED:
        result = qa_png(PACK / relative)
        component_qa[relative] = result
        if any(result["corner_alpha"]):
            raise SystemExit(f"Nontransparent corner in {relative}: {result['corner_alpha']}")
        if result["magenta_fringe_pixels"]:
            raise SystemExit(f"Magenta fringe in {relative}: {result['magenta_fringe_pixels']}")

    files: dict[str, str] = {}
    for path in sorted(PACK.rglob("*")):
        if path.is_file() and path != MANIFEST and path.name != ".DS_Store":
            files[str(path.relative_to(PACK))] = sha256(path)

    manifest = {
        "schema_version": 1,
        "gate": "G03_remaining_non_character_stall_attachments",
        "status": "candidate_pending_founder_approval",
        "runtime_promoted": False,
        "main_character_in_scope": False,
        "generation": {
            "preserved_usable_outputs": 9,
            "built_in_imagegen_invocations": 10,
            "delivery_failures": 1,
            "note": "The first stockpot call completed but returned no surfaced image payload; the exact request was retried once and only the surfaced result is preserved.",
        },
        "qa": {
            "expected_components": len(EXPECTED),
            "transparent_corner_failures": 0,
            "magenta_fringe_failures": 0,
            "components": component_qa,
        },
        "known_review_flags": [
            "Founder must judge all registered sizes and proportions.",
            "Rank plaque v001 is clean but brown; generated/local recolor v002 is rejected and must not ship.",
            "Counter lantern OFF glass is honey-amber and may read faintly luminous.",
            "Warm light spill across stall wood remains deferred.",
        ],
        "files_sha256": files,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(EXPECTED)} transparent components")
    print("Transparent corners: PASS")
    print("Magenta fringe: PASS")
    print(MANIFEST)


if __name__ == "__main__":
    main()
