#!/usr/bin/env python3
"""Promote the approved V004 stall attachment kit into Godot runtime assets.

The immutable source-art candidates remain untouched. Runtime derivatives are
transparent RGBA PNGs sized for a 2x version of the 720 x 1280 logical canvas.
Review-only assembled previews and the rejected green plaque experiment are
intentionally absent from this builder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (
    REPO_ROOT
    / "art/source-assets/home-menu/stall/v004-attachment-kit"
)
OUTPUT_ROOT = (
    REPO_ROOT
    / "game/assets/environments/home_village/v001/stall/attachments/v004"
)
PLACEMENT_CONTRACT = SOURCE_ROOT / "placement-and-motion-contract.json"
SOURCE_MANIFEST = SOURCE_ROOT / "manifest.json"

RUNTIME_SCALE = 2
BUTTON_INTERMEDIATE_SIZE = (692, 410)
BUTTON_NINE_PATCH_INSETS = {
    "left": 144,
    "top": 104,
    "right": 144,
    "bottom": 104,
}
PLAQUE_TARGET_SIZE = (456, 96)
PLAQUE_SOURCE_CAPS = (185, 185)


@dataclass(frozen=True)
class AssetSpec:
    asset_id: str
    source: str
    output: str
    operation: str
    output_size: tuple[int, int] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _twice(width: int, height: int) -> tuple[int, int]:
    return width * RUNTIME_SCALE, height * RUNTIME_SCALE


# The independent bottle pieces came from the same authored sheet. Scaling all
# of them from the empty-crate width keeps their relative visual proportions,
# while the empty crate lands exactly on the 2x 117 px logical group width.
BOTTLE_KIT_SCALE = _twice(117, 101)[0] / 501.0


ASSETS: tuple[AssetSpec, ...] = (
    AssetSpec(
        "stockpot.body_open",
        "stockpot/components/stall_stockpot_body_open_candidate_v001.png",
        "stockpot/stall_stockpot_body_open_v001.png",
        "resize_exact",
        _twice(86, 92),
        {"logical_box": [136, 626, 86, 92]},
    ),
    AssetSpec(
        "stockpot.lid",
        "stockpot/components/stall_stockpot_lid_candidate_v001.png",
        "stockpot/stall_stockpot_lid_v001.png",
        "resize_exact",
        _twice(90, 49),
        {"logical_box": [133, 589, 90, 49], "logical_pivot": [178, 625]},
    ),
    AssetSpec(
        "stockpot.contact_shadow",
        "stockpot/components/stall_stockpot_contact_shadow_candidate_v001.png",
        "stockpot/stall_stockpot_contact_shadow_v001.png",
        "resize_exact",
        _twice(94, 18),
        {"logical_box": [132, 709, 94, 18]},
    ),
    AssetSpec(
        "counter_lantern.body_off",
        "counter-small/cutouts/counter-oil-lantern-body-off-candidate-v001.png",
        "counter_lantern/counter-oil-lantern-body-off-v001.png",
        "resize_exact",
        _twice(63, 115),
        {"logical_box": [209, 604, 63, 115]},
    ),
    AssetSpec(
        "counter_lantern.core_add",
        "counter-small/cutouts/counter-oil-lantern-core-add-candidate-v001.png",
        "counter_lantern/counter-oil-lantern-core-add-v001.png",
        "resize_exact",
        _twice(31, 58),
        {"logical_box": [225, 646, 31, 58]},
    ),
    AssetSpec(
        "counter_lantern.halo_add",
        "counter-small/cutouts/counter-oil-lantern-halo-add-candidate-v001.png",
        "counter_lantern/counter-oil-lantern-halo-add-v001.png",
        "resize_exact",
        _twice(110, 146),
        {"logical_box": [186, 581, 110, 146], "registered_alpha": 0.55},
    ),
    AssetSpec(
        "counter_lantern.contact_shadow",
        "counter-small/cutouts/counter-oil-lantern-contact-shadow-candidate-v001.png",
        "counter_lantern/counter-oil-lantern-contact-shadow-v001.png",
        "resize_exact",
        _twice(72, 18),
        {"logical_box": [205, 704, 72, 18]},
    ),
    AssetSpec(
        "food_bowl.grape",
        "counter-small/cutouts/grape-food-bowl-candidate-v001.png",
        "food_bowl/grape-food-bowl-v001.png",
        "resize_exact",
        _twice(66, 66),
        {"logical_box": [157, 652, 66, 66]},
    ),
    AssetSpec(
        "counter_plant.pot",
        "counter-decor/components/counter_plant_pot_candidate_v001.png",
        "counter_plant/counter_plant_pot_v001.png",
        "resize_exact",
        _twice(67, 75),
        {"logical_box": [481, 644, 67, 75]},
    ),
    AssetSpec(
        "counter_plant.foliage",
        "counter-decor/components/counter_plant_foliage_candidate_v001.png",
        "counter_plant/counter_plant_foliage_v001.png",
        "resize_exact",
        _twice(61, 154),
        {"logical_box": [486, 500, 61, 154]},
    ),
    AssetSpec(
        "bottle_crate.empty",
        "counter-decor/components/bottle_crate_empty_candidate_v001.png",
        "bottle_crate/bottle_crate_empty_v001.png",
        "resize_exact",
        (
            round(501 * BOTTLE_KIT_SCALE),
            round(379 * BOTTLE_KIT_SCALE),
        ),
        {"shared_kit_scale": BOTTLE_KIT_SCALE},
    ),
    AssetSpec(
        "bottle_crate.bottle_brown",
        "counter-decor/components/bottle_brown_candidate_v001.png",
        "bottle_crate/bottle_brown_v001.png",
        "resize_exact",
        (
            round(164 * BOTTLE_KIT_SCALE),
            round(303 * BOTTLE_KIT_SCALE),
        ),
        {"shared_kit_scale": BOTTLE_KIT_SCALE},
    ),
    AssetSpec(
        "bottle_crate.bottle_green",
        "counter-decor/components/bottle_green_candidate_v001.png",
        "bottle_crate/bottle_green_v001.png",
        "resize_exact",
        (
            round(175 * BOTTLE_KIT_SCALE),
            round(332 * BOTTLE_KIT_SCALE),
        ),
        {"shared_kit_scale": BOTTLE_KIT_SCALE},
    ),
    AssetSpec(
        "bottle_crate.bottle_cream_blue_cap",
        "counter-decor/components/bottle_cream_blue_cap_candidate_v001.png",
        "bottle_crate/bottle_cream_blue_cap_v001.png",
        "resize_exact",
        (
            round(184 * BOTTLE_KIT_SCALE),
            round(306 * BOTTLE_KIT_SCALE),
        ),
        {"shared_kit_scale": BOTTLE_KIT_SCALE},
    ),
    AssetSpec(
        "counter_cloth.red_draped",
        "counter-decor/components/counter_cloth_red_draped_candidate_v001.png",
        "counter_cloth/counter_cloth_red_draped_v001.png",
        "resize_exact",
        _twice(97, 120),
        {"logical_box": [517, 684, 97, 120]},
    ),
    AssetSpec(
        "rank.plaque_empty_sockets",
        "ui/components/rank/rank-plaque-empty-sockets-v001.png",
        "ui/rank/rank-plaque-empty-sockets-v001.png",
        "horizontal_nine_slice",
        PLAQUE_TARGET_SIZE,
        {
            "logical_box": [246, 372, 228, 48],
            "source_caps_px": list(PLAQUE_SOURCE_CAPS),
        },
    ),
    AssetSpec(
        "rank.star_empty",
        "ui/components/rank/rank-star-empty-v001.png",
        "ui/rank/rank-star-empty-v001.png",
        "resize_exact",
        _twice(42, 34),
        {"logical_size": [42, 34]},
    ),
    AssetSpec(
        "rank.star_filled",
        "ui/components/rank/rank-star-filled-v001.png",
        "ui/rank/rank-star-filled-v001.png",
        "resize_exact",
        _twice(42, 34),
        {"logical_size": [42, 34]},
    ),
    AssetSpec(
        "rank.star_shine",
        "ui/components/rank/rank-star-shine-v001.png",
        "ui/rank/rank-star-shine-v001.png",
        "resize_exact",
        (42, 40),
        {"sized_relative_to_runtime_star": True},
    ),
    AssetSpec(
        "button.primary_normal",
        "ui/components/buttons/menu-button-primary-normal-v001.png",
        "ui/buttons/menu-button-primary-normal-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "primary", "state": "normal"},
    ),
    AssetSpec(
        "button.primary_selected",
        "ui/components/buttons/menu-button-primary-selected-v001.png",
        "ui/buttons/menu-button-primary-selected-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "primary", "state": "selected"},
    ),
    AssetSpec(
        "button.primary_pressed",
        "ui/components/buttons/menu-button-primary-pressed-v001.png",
        "ui/buttons/menu-button-primary-pressed-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "primary", "state": "pressed"},
    ),
    AssetSpec(
        "button.primary_disabled",
        "ui/components/buttons/menu-button-primary-disabled-v001.png",
        "ui/buttons/menu-button-primary-disabled-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "primary", "state": "disabled"},
    ),
    AssetSpec(
        "button.secondary_normal",
        "ui/components/buttons/menu-button-secondary-normal-v001.png",
        "ui/buttons/menu-button-secondary-normal-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "secondary", "state": "normal"},
    ),
    AssetSpec(
        "button.secondary_selected",
        "ui/components/buttons/menu-button-secondary-selected-v001.png",
        "ui/buttons/menu-button-secondary-selected-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "secondary", "state": "selected"},
    ),
    AssetSpec(
        "button.secondary_pressed",
        "ui/components/buttons/menu-button-secondary-pressed-v001.png",
        "ui/buttons/menu-button-secondary-pressed-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "secondary", "state": "pressed"},
    ),
    AssetSpec(
        "button.secondary_disabled",
        "ui/components/buttons/menu-button-secondary-disabled-v001.png",
        "ui/buttons/menu-button-secondary-disabled-v001.png",
        "resize_exact",
        BUTTON_INTERMEDIATE_SIZE,
        {"role": "secondary", "state": "disabled"},
    ),
    AssetSpec(
        "button.leaf_left",
        "ui/components/buttons/menu-button-leaf-left-v001.png",
        "ui/buttons/menu-button-leaf-left-v001.png",
        "copy_lossless",
        (206, 207),
        {"detached_ornament": True},
    ),
    AssetSpec(
        "button.leaf_right",
        "ui/components/buttons/menu-button-leaf-right-v001.png",
        "ui/buttons/menu-button-leaf-right-v001.png",
        "copy_lossless",
        (206, 208),
        {"detached_ornament": True},
    ),
    AssetSpec(
        "settings.normal",
        "ui/components/settings/settings-cog-normal-v001.png",
        "ui/settings/settings-cog-normal-v001.png",
        "contain_bottom",
        _twice(75, 84),
        {"logical_box": [515, 1033, 75, 84], "state": "normal"},
    ),
    AssetSpec(
        "settings.pressed",
        "ui/components/settings/settings-cog-pressed-v001.png",
        "ui/settings/settings-cog-pressed-v001.png",
        "contain_bottom",
        _twice(75, 84),
        {"logical_box": [515, 1033, 75, 84], "state": "pressed"},
    ),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _open_rgba(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGBA")


def _resize_rgba(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    if image.size == size:
        return image.copy()
    # Pillow's RGBa mode resamples premultiplied color and alpha together,
    # preventing invisible edge colors from bleeding into translucent pixels.
    resized = (
        image.convert("RGBa")
        .resize(size, Image.Resampling.LANCZOS)
        .convert("RGBA")
    )
    # Very-low-alpha LANCZOS ringing can unpremultiply a one-digit alpha value
    # into a saturated color that was not visible in the source art. Remove
    # only those near-invisible magenta-key remnants; meaningful soft alpha and
    # all ordinary painted colors remain untouched.
    cleaned_pixels: list[tuple[int, int, int, int]] = []
    for red, green, blue, alpha in resized.get_flattened_data():
        if (
            alpha <= 16
            and red > 170
            and blue > 170
            and green < 90
        ):
            cleaned_pixels.append((0, 0, 0, 0))
        else:
            cleaned_pixels.append((red, green, blue, alpha))
    resized.putdata(cleaned_pixels)
    return resized


def _contain_bottom(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = min(size[0] / image.width, size[1] / image.height)
    fitted = _resize_rgba(
        image,
        (
            max(1, round(image.width * scale)),
            max(1, round(image.height * scale)),
        ),
    )
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.alpha_composite(
        fitted,
        ((size[0] - fitted.width) // 2, size[1] - fitted.height),
    )
    return output


def _horizontal_nine_slice(
    image: Image.Image,
    size: tuple[int, int],
    source_caps: tuple[int, int],
) -> tuple[Image.Image, tuple[int, int]]:
    target_width, target_height = size
    height_scale = target_height / image.height
    scaled = _resize_rgba(
        image,
        (max(1, round(image.width * height_scale)), target_height),
    )
    left_cap = max(1, round(source_caps[0] * height_scale))
    right_cap = max(1, round(source_caps[1] * height_scale))
    if left_cap + right_cap >= min(target_width, scaled.width):
        raise ValueError(
            "Nine-slice caps do not leave a stretchable center: "
            f"caps={(left_cap, right_cap)} target={size} scaled={scaled.size}"
        )

    output = Image.new("RGBA", size, (0, 0, 0, 0))
    left = scaled.crop((0, 0, left_cap, target_height))
    center = scaled.crop(
        (left_cap, 0, scaled.width - right_cap, target_height)
    )
    right = scaled.crop(
        (scaled.width - right_cap, 0, scaled.width, target_height)
    )
    center_width = target_width - left_cap - right_cap
    output.alpha_composite(left, (0, 0))
    output.alpha_composite(
        _resize_rgba(center, (center_width, target_height)),
        (left_cap, 0),
    )
    output.alpha_composite(right, (target_width - right_cap, 0))
    return output, (left_cap, right_cap)


def _build_image(spec: AssetSpec, source: Image.Image) -> tuple[Image.Image, dict[str, Any]]:
    if spec.output_size is None:
        raise ValueError(f"Missing output size for {spec.asset_id}")

    transform_metadata: dict[str, Any] = {}
    if spec.operation == "resize_exact":
        output = _resize_rgba(source, spec.output_size)
    elif spec.operation == "copy_lossless":
        if source.size != spec.output_size:
            raise ValueError(
                f"Copy size mismatch for {spec.asset_id}: "
                f"{source.size} != {spec.output_size}"
            )
        output = source.copy()
    elif spec.operation == "contain_bottom":
        output = _contain_bottom(source, spec.output_size)
        alpha_bounds = output.getchannel("A").getbbox()
        transform_metadata["contained_alpha_bounds_px"] = (
            list(alpha_bounds) if alpha_bounds is not None else None
        )
    elif spec.operation == "horizontal_nine_slice":
        output, runtime_caps = _horizontal_nine_slice(
            source,
            spec.output_size,
            PLAQUE_SOURCE_CAPS,
        )
        transform_metadata["runtime_horizontal_caps_px"] = list(runtime_caps)
    else:
        raise ValueError(f"Unknown operation for {spec.asset_id}: {spec.operation}")
    return output, transform_metadata


def _save_png(image: Image.Image, path: Path) -> None:
    if image.mode != "RGBA":
        raise ValueError(f"Runtime image must be RGBA before save: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True, compress_level=9)


def _qa_png(path: Path, expected_size: tuple[int, int]) -> dict[str, Any]:
    with Image.open(path) as loaded:
        mode = loaded.mode
        image = loaded.convert("RGBA")
    if mode != "RGBA":
        raise RuntimeError(f"Runtime PNG is not stored as RGBA: {path} ({mode})")
    if image.size != expected_size:
        raise RuntimeError(
            f"Runtime PNG has wrong dimensions: {path} "
            f"{image.size} != {expected_size}"
        )

    alpha = image.getchannel("A")
    alpha_bounds = alpha.getbbox()
    if alpha_bounds is None:
        raise RuntimeError(f"Runtime PNG is fully transparent: {path}")
    pixels = list(image.get_flattened_data())
    corners = [
        image.getpixel((0, 0))[3],
        image.getpixel((image.width - 1, 0))[3],
        image.getpixel((0, image.height - 1))[3],
        image.getpixel((image.width - 1, image.height - 1))[3],
    ]
    if any(corners):
        raise RuntimeError(f"Runtime PNG has opaque corner pixels: {path} {corners}")

    transparent_pixels = 0
    partial_alpha_pixels = 0
    opaque_pixels = 0
    magenta_fringe_pixels = 0
    for red, green, blue, alpha_value in pixels:
        if alpha_value == 0:
            transparent_pixels += 1
        elif alpha_value == 255:
            opaque_pixels += 1
        else:
            partial_alpha_pixels += 1
        if alpha_value > 0 and red > 170 and blue > 170 and green < 90:
            magenta_fringe_pixels += 1
    if magenta_fringe_pixels:
        raise RuntimeError(
            f"Runtime PNG has visible magenta fringe pixels: "
            f"{path} ({magenta_fringe_pixels})"
        )

    return {
        "stored_mode": mode,
        "size_px": list(image.size),
        "alpha_bounds_px": list(alpha_bounds),
        "corner_alpha": corners,
        "transparent_pixels": transparent_pixels,
        "partial_alpha_pixels": partial_alpha_pixels,
        "opaque_pixels": opaque_pixels,
        "magenta_fringe_pixels": magenta_fringe_pixels,
    }


def _assert_no_unmanaged_pngs() -> None:
    expected = {OUTPUT_ROOT / spec.output for spec in ASSETS}
    existing = set(OUTPUT_ROOT.rglob("*.png")) if OUTPUT_ROOT.exists() else set()
    unexpected = sorted(existing - expected)
    if unexpected:
        paths = "\n- ".join(path.as_posix() for path in unexpected)
        raise RuntimeError(
            "Refusing to delete or silently retain unmanaged V004 PNGs:\n- " + paths
        )


def _validate_source_manifest_hashes() -> None:
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    hashes = manifest.get("files_sha256")
    if not isinstance(hashes, dict) or not hashes:
        raise RuntimeError("Source manifest files_sha256 must be a non-empty object")

    failures: list[str] = []
    for relative_path, expected in sorted(hashes.items()):
        source_path = SOURCE_ROOT / relative_path
        if not source_path.is_file():
            failures.append(f"missing: {relative_path}")
            continue
        actual = _sha256(source_path)
        if actual != expected:
            failures.append(
                f"hash mismatch: {relative_path} expected {expected}, got {actual}"
            )
    if failures:
        raise RuntimeError(
            "Source manifest integrity validation failed:\n- " + "\n- ".join(failures)
        )


def main() -> None:
    required = [PLACEMENT_CONTRACT, SOURCE_MANIFEST]
    required.extend(SOURCE_ROOT / spec.source for spec in ASSETS)
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("\n".join(path.as_posix() for path in missing))

    if len({spec.asset_id for spec in ASSETS}) != len(ASSETS):
        raise RuntimeError("Duplicate runtime asset_id in ASSETS")
    if len({spec.output for spec in ASSETS}) != len(ASSETS):
        raise RuntimeError("Duplicate runtime output path in ASSETS")
    _validate_source_manifest_hashes()
    _assert_no_unmanaged_pngs()

    built: list[dict[str, Any]] = []
    for spec in ASSETS:
        source_path = SOURCE_ROOT / spec.source
        output_path = OUTPUT_ROOT / spec.output
        source = _open_rgba(source_path)
        output, transform_metadata = _build_image(spec, source)
        _save_png(output, output_path)
        qa = _qa_png(output_path, spec.output_size or output.size)
        built.append(
            {
                "asset_id": spec.asset_id,
                "source": source_path.relative_to(REPO_ROOT).as_posix(),
                "source_sha256": _sha256(source_path),
                "source_size_px": list(source.size),
                "output": output_path.relative_to(REPO_ROOT).as_posix(),
                "output_sha256": _sha256(output_path),
                "operation": spec.operation,
                "metadata": {**spec.metadata, **transform_metadata},
                "qa": qa,
            }
        )

    placement_contract = json.loads(PLACEMENT_CONTRACT.read_text(encoding="utf-8"))
    manifest = {
        "schema_version": 1,
        "asset_id": "env.home_village.stall.attachments.runtime.v004",
        "status": "founder_approved_runtime_derivatives",
        "source_gate": "G03_remaining_non_character_stall_attachments",
        "source_pack": SOURCE_ROOT.relative_to(REPO_ROOT).as_posix(),
        "source_manifest_sha256": _sha256(SOURCE_MANIFEST),
        "placement_contract": PLACEMENT_CONTRACT.relative_to(REPO_ROOT).as_posix(),
        "placement_contract_sha256": _sha256(PLACEMENT_CONTRACT),
        "coordinate_contract": {
            "logical_canvas_px": placement_contract["logical_canvas"],
            "runtime_resolution_scale": RUNTIME_SCALE,
            "runtime_canvas_px": [
                value * RUNTIME_SCALE
                for value in placement_contract["logical_canvas"]
            ],
            "coordinate_space": placement_contract["coordinate_space"],
            "shared_stage": placement_contract["shared_stage"],
        },
        "processing": {
            "color_mode": "RGBA",
            "resampler": "Pillow Image.Resampling.LANCZOS",
            "alpha_resampling": "premultiplied RGBa",
            "png": {
                "lossless": True,
                "optimize": True,
                "compress_level": 9,
            },
            "buttons": {
                "normalized_intermediate_px": list(BUTTON_INTERMEDIATE_SIZE),
                "recommended_nine_patch_insets_px": BUTTON_NINE_PATCH_INSETS,
                "labels_baked_into_art": False,
            },
            "rank_plaque": {
                "runtime_size_px": list(PLAQUE_TARGET_SIZE),
                "horizontal_nine_slice_source_caps_px": list(
                    PLAQUE_SOURCE_CAPS
                ),
            },
        },
        "assembly_contract": {
            "stockpot": placement_contract["attachments"]["stockpot"],
            "counter_lantern": {
                **placement_contract["attachments"]["counter_lantern"],
                "component_logical_boxes": {
                    "halo_add": [186, 581, 110, 146],
                    "body_off": [209, 604, 63, 115],
                    "core_add": [225, 646, 31, 58],
                    "contact_shadow": [205, 704, 72, 18],
                },
            },
            "food_bowl": placement_contract["attachments"]["food_bowl"],
            "counter_plant": {
                **placement_contract["attachments"]["counter_plant"],
                "component_logical_boxes": {
                    "foliage": [486, 500, 61, 154],
                    "pot": [481, 644, 67, 75],
                },
            },
            "bottle_crate": {
                **placement_contract["attachments"]["bottle_crate"],
                "shared_runtime_source_scale": BOTTLE_KIT_SCALE,
                "runtime_group_envelope_px": list(_twice(117, 101)),
                "assembly_registration": "deferred_to_prefab_integration",
            },
            "counter_cloth": placement_contract["attachments"]["counter_cloth"],
            "rank_plaque": placement_contract["attachments"]["rank_plaque"],
            "menu_buttons": placement_contract["attachments"]["menu_buttons"],
            "settings_control": placement_contract["attachments"]["settings_control"],
        },
        "excluded": [
            {
                "pattern": "*assembled_preview*",
                "reason": "review-only composites; runtime uses modular pieces",
            },
            {
                "pattern": "ui/generated/rank-plaque-kit-chroma-v002.png",
                "reason": "rejected green plaque recolor",
            },
            {
                "pattern": "ui/transparent/rank-plaque-kit-cutout-v002.png",
                "reason": "rejected green plaque recolor derivative",
            },
            {
                "pattern": "ui/masks/rank-plaque-face-recolor-mask-v002.png",
                "reason": "rejected green plaque recolor mask",
            },
            {
                "pattern": "fonts/*",
                "reason": "labels remain native Godot text; this promotion adds no font",
            },
            {
                "pattern": "steam_or_smoke_raster_art",
                "reason": "steam and smoke remain procedural runtime effects",
            },
            {
                "pattern": "main_character/*",
                "reason": "main Bentosaur character is outside V004 scope",
            },
        ],
        "asset_count": len(built),
        "assets": built,
        "builder": "tools/art/promote_stall_attachment_runtime_v004.py",
    }

    manifest_path = OUTPUT_ROOT / "runtime_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Promoted {len(built)} V004 runtime PNGs")
    print("RGBA / transparent-corner / magenta-fringe validation: PASS")
    for item in built:
        print(f"- {item['output']} {item['qa']['size_px']}")
    print(f"- {manifest_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
