#!/usr/bin/env python3
"""Derive registered additive lighting layers from an unlit base and look target.

The look target may have been repainted by a generative edit. This tool keeps the
approved base immutable and transfers only strong warm positive-light deltas.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--prefix", default="home-village")
    parser.add_argument(
        "--floor-boundary",
        default=(
            "0:650,75:657,165:648,255:628,330:596,395:566,450:548,"
            "500:548,555:568,610:604,680:632,760:651,850:660,940:666"
        ),
        help="Comma-separated x:y points describing the architecture/floor edge.",
    )
    return parser.parse_args()


def srgb_to_linear(value: np.ndarray) -> np.ndarray:
    return np.where(
        value <= 0.04045,
        value / 12.92,
        ((value + 0.055) / 1.055) ** 2.4,
    )


def linear_to_srgb(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return np.where(
        value <= 0.0031308,
        value * 12.92,
        1.055 * np.power(value, 1.0 / 2.4) - 0.055,
    )


def smoothstep(edge0: float, edge1: float, value: np.ndarray) -> np.ndarray:
    unit = np.clip((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return unit * unit * (3.0 - 2.0 * unit)


def load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def parse_boundary(spec: str, width: int) -> np.ndarray:
    points = []
    for item in spec.split(","):
        x_text, y_text = item.split(":", maxsplit=1)
        points.append((float(x_text), float(y_text)))
    points.sort()
    x_values = np.arange(width, dtype=np.float32)
    return np.interp(
        x_values,
        np.asarray([point[0] for point in points]),
        np.asarray([point[1] for point in points]),
    )


def soften_support(signal: np.ndarray) -> np.ndarray:
    seed = (signal >= 0.36).astype(np.uint8) * 255
    seed_image = Image.fromarray(seed, mode="L")
    expanded = seed_image.filter(ImageFilter.MaxFilter(9))
    softened = expanded.filter(ImageFilter.GaussianBlur(radius=9))
    halo = np.asarray(softened, dtype=np.float32) / 255.0
    return np.maximum(signal, halo * 0.82)


def blur_mask(mask: np.ndarray, radius: float) -> np.ndarray:
    image = Image.fromarray(
        np.round(np.clip(mask, 0.0, 1.0) * 255.0).astype(np.uint8),
        mode="L",
    )
    blurred = image.filter(ImageFilter.GaussianBlur(radius=radius))
    return np.asarray(blurred, dtype=np.float32) / 255.0


def encode_additive_layer(contribution_linear: np.ndarray) -> Image.Image:
    contribution_linear = np.clip(contribution_linear, 0.0, 1.0)
    alpha = np.max(contribution_linear, axis=2)
    straight_linear = np.divide(
        contribution_linear,
        np.maximum(alpha[..., None], 1e-6),
        out=np.zeros_like(contribution_linear),
        where=alpha[..., None] > 1e-6,
    )
    straight_srgb = linear_to_srgb(straight_linear)
    rgba = np.dstack((straight_srgb, alpha))
    return Image.fromarray(np.round(rgba * 255.0).astype(np.uint8), mode="RGBA")


def save_rgb(path: Path, rgb: np.ndarray) -> None:
    image = Image.fromarray(
        np.round(np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8),
        mode="RGB",
    )
    image.save(path)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    base_srgb = load_rgb(args.base)
    target_srgb = load_rgb(args.target)
    if base_srgb.shape != target_srgb.shape:
        raise SystemExit(
            f"Image dimensions differ: {base_srgb.shape} vs {target_srgb.shape}"
        )

    height, width, _ = base_srgb.shape
    base_linear = srgb_to_linear(base_srgb)
    target_linear = srgb_to_linear(target_srgb)
    positive_delta = np.maximum(target_linear - base_linear, 0.0)

    delta_luma = np.tensordot(
        positive_delta,
        np.asarray([0.2126, 0.7152, 0.0722], dtype=np.float32),
        axes=([2], [0]),
    )
    target_warmth = (
        target_linear[..., 0] * 0.58
        + target_linear[..., 1] * 0.42
        - target_linear[..., 2]
    )
    delta_warmth = (
        positive_delta[..., 0] * 0.58
        + positive_delta[..., 1] * 0.42
        - positive_delta[..., 2] * 0.65
    )

    light_signal = (
        smoothstep(0.008, 0.075, delta_luma)
        * smoothstep(0.012, 0.20, target_warmth)
        * smoothstep(0.004, 0.11, delta_warmth)
    )
    support = soften_support(light_signal)
    warm_contribution = positive_delta * support[..., None]

    boundary = parse_boundary(args.floor_boundary, width)
    y_values = np.arange(height, dtype=np.float32)[:, None]
    floor_weight = smoothstep(-10.0, 24.0, y_values - boundary[None, :])
    architecture_weight = 1.0 - floor_weight

    architecture_contribution = warm_contribution * architecture_weight[..., None]
    reflection_contribution = warm_contribution * floor_weight[..., None]

    target_luma = np.tensordot(
        target_linear,
        np.asarray([0.2126, 0.7152, 0.0722], dtype=np.float32),
        axes=([2], [0]),
    )
    core_weight = (
        smoothstep(0.17, 0.55, target_luma)
        * smoothstep(0.06, 0.30, target_warmth)
        * architecture_weight
    )
    core_contribution = architecture_contribution * core_weight[..., None]
    residual_architecture = np.maximum(
        architecture_contribution - core_contribution,
        0.0,
    )
    halo_weight = (
        smoothstep(0.008, 0.22, blur_mask(core_weight, radius=20.0))
        * (1.0 - core_weight)
        * architecture_weight
    )
    halo_contribution = residual_architecture * halo_weight[..., None]
    spill_contribution = np.maximum(
        residual_architecture - halo_contribution,
        0.0,
    )

    layers = {
        "light-cores": core_contribution,
        "light-halos": halo_contribution,
        "indirect-warm-spill": spill_contribution,
        "warm-reflections": reflection_contribution,
    }
    for layer_name, contribution in layers.items():
        layer_path = args.out_dir / f"{args.prefix}-{layer_name}.png"
        encode_additive_layer(contribution).save(layer_path)

    reconstructed_linear = np.clip(
        base_linear
        + core_contribution
        + halo_contribution
        + spill_contribution
        + reflection_contribution,
        0.0,
        1.0,
    )
    reconstructed_srgb = linear_to_srgb(reconstructed_linear)
    preview_path = args.out_dir / f"{args.prefix}-registered-composite-preview.png"
    save_rgb(preview_path, reconstructed_srgb)

    mask_preview = np.dstack(
        (
            np.clip(core_weight, 0.0, 1.0),
            np.clip(support * architecture_weight, 0.0, 1.0),
            np.clip(support * floor_weight, 0.0, 1.0),
        )
    )
    save_rgb(args.out_dir / f"{args.prefix}-mask-diagnostic.png", mask_preview)

    report = {
        "base": str(args.base),
        "look_target": str(args.target),
        "width": width,
        "height": height,
        "blend_mode": "add",
        "layer_order": [
            f"{args.prefix}-indirect-warm-spill.png",
            f"{args.prefix}-light-halos.png",
            f"{args.prefix}-light-cores.png",
            f"{args.prefix}-warm-reflections.png",
        ],
        "motion_policy": {
            "light-cores": "eligible for subtle procedural flicker",
            "light-halos": "eligible for lower-amplitude synchronized flicker",
            "indirect-warm-spill": "fade on once, then remain stable",
            "warm-reflections": "fade on once; only a future isolated shimmer subset should flicker"
        },
        "floor_boundary": args.floor_boundary,
        "coverage": {
            name: float(np.count_nonzero(np.max(value, axis=2) > 1e-4))
            / float(width * height)
            for name, value in layers.items()
        },
        "notes": [
            "All outputs are pixel-registered to the approved unlit master.",
            "RGBA layers encode straight-alpha additive contributions.",
            "Use an additive canvas blend mode; do not normal-alpha composite them.",
            "The generative look target remains review-only and is not used as a base.",
            "Do not continuously flicker broad spill or reflection layers.",
        ],
    }
    (args.out_dir / f"{args.prefix}-extraction-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
