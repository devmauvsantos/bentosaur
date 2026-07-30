#!/usr/bin/env python3
"""Build evidence boards, cross-run comparisons, and SHA-256 manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


SUPPORTED_HASH_SUFFIXES = {
    ".blend",
    ".json",
    ".md",
    ".png",
    ".py",
    ".log",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path(
            "/System/Library/Fonts/Supplemental/"
            + ("Arial Bold.ttf" if bold else "Arial.ttf")
        ),
        Path(
            "/System/Library/Fonts/"
            + ("Helvetica.ttc" if bold else "Helvetica.ttc")
        ),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(candidate.as_posix(), size=size)
            except OSError:
                pass
    return ImageFont.load_default()


FONT_TITLE = font(34, bold=True)
FONT_HEADING = font(24, bold=True)
FONT_BODY = font(19)
FONT_SMALL = font(15)


def fit_image(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (19, 27, 40))
    x = (size[0] - image.width) // 2
    y = (size[1] - image.height) // 2
    canvas.paste(image, (x, y))
    return canvas


def pose_label(pose: dict[str, Any]) -> str:
    result = "PASS" if pose["diagnostic_pass"] else "FAIL"
    flags = pose.get("threshold_flags", [])
    regions = sorted({flag["region"] for flag in flags})
    if not regions:
        return result
    noun = "region" if len(regions) == 1 else "regions"
    return f"{result} · {len(regions)} flagged {noun}"


def build_contact_board(run: Path, report: dict[str, Any]) -> Path:
    poses = list(report["poses"].items())
    views = report["render"]["views"]
    cell = (400, 400)
    left = 250
    top = 125
    row_h = cell[1] + 70
    width = left + len(views) * cell[0] + 35
    height = top + len(poses) * row_h + 25
    board = Image.new("RGB", (width, height), (12, 18, 29))
    draw = ImageDraw.Draw(board)
    draw.text((28, 24), "G40 deformation-validation contact sheet", font=FONT_TITLE, fill=(238, 242, 247))
    draw.text(
        (28, 72),
        f"{report['candidate']['label']} · bounded diagnostic rig · not production approval",
        font=FONT_BODY,
        fill=(170, 182, 198),
    )
    for column, view in enumerate(views):
        draw.text(
            (left + column * cell[0] + 14, top - 38),
            view["name"].replace("_", " ").title(),
            font=FONT_HEADING,
            fill=(210, 220, 232),
        )
    for row, (pose_name, pose) in enumerate(poses):
        y = top + row * row_h
        status_color = (107, 214, 151) if pose["diagnostic_pass"] else (255, 125, 115)
        draw.text((28, y + 10), pose_name.replace("_", " ").title(), font=FONT_HEADING, fill=(238, 242, 247))
        draw.text((28, y + 49), pose_label(pose), font=FONT_SMALL, fill=status_color)
        for column, view in enumerate(views):
            path = Path(pose["renders"][view["name"]])
            image = fit_image(path, cell)
            board.paste(image, (left + column * cell[0], y))
    output = run / "evidence" / "pose_contact_sheet.png"
    board.save(output, optimize=True)
    return output


def build_neutral_comparison(run: Path, report: dict[str, Any]) -> Path:
    poses = report["poses"]
    neutral_name = next(
        (name for name, value in poses.items() if value.get("is_neutral")),
        next(iter(poses)),
    )
    neutral = poses[neutral_name]
    view_name = report["render"]["comparison_view"]
    rows = [(name, pose) for name, pose in poses.items() if name != neutral_name]
    cell = (520, 520)
    left = 220
    top = 120
    row_h = 575
    width = left + cell[0] * 2 + 40
    height = top + max(1, len(rows)) * row_h + 20
    board = Image.new("RGB", (width, height), (12, 18, 29))
    draw = ImageDraw.Draw(board)
    draw.text((28, 22), "Neutral vs posed deformation comparison", font=FONT_TITLE, fill=(238, 242, 247))
    draw.text((left + 20, 76), neutral_name.replace("_", " ").title(), font=FONT_HEADING, fill=(190, 207, 226))
    draw.text((left + cell[0] + 20, 76), "Stress pose", font=FONT_HEADING, fill=(190, 207, 226))
    if not rows:
        rows = [(neutral_name, neutral)]
    neutral_image = fit_image(Path(neutral["renders"][view_name]), cell)
    for row, (name, pose) in enumerate(rows):
        y = top + row * row_h
        status_color = (107, 214, 151) if pose["diagnostic_pass"] else (255, 125, 115)
        draw.text((28, y + 12), name.replace("_", " ").title(), font=FONT_HEADING, fill=(238, 242, 247))
        draw.text((28, y + 50), pose_label(pose), font=FONT_SMALL, fill=status_color)
        board.paste(neutral_image, (left, y))
        board.paste(fit_image(Path(pose["renders"][view_name]), cell), (left + cell[0], y))
    output = run / "evidence" / "neutral_vs_poses.png"
    board.save(output, optimize=True)
    return output


def build_boards(run: Path) -> None:
    report_path = run / "reports" / "validation_report.json"
    report = load_json(report_path)
    outputs = [
        build_contact_board(run, report),
        build_neutral_comparison(run, report),
    ]
    payload = {
        "schema_version": "1.0.0",
        "diagnostic_only": True,
        "boards": [path.as_posix() for path in outputs],
        "notice": (
            "Evidence boards support inspection; they do not replace visual "
            "review or user approval."
        ),
    }
    (run / "reports" / "evidence_index.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, sort_keys=True))


def compact_pose_metrics(pose: dict[str, Any]) -> dict[str, Any]:
    return {
        "diagnostic_pass": pose["diagnostic_pass"],
        "flagged_regions": sorted(
            {flag["region"] for flag in pose.get("threshold_flags", [])}
        ),
        "regions": {
            name: {
                "face_area_p05": value["face_area_ratio"]["p05"],
                "face_area_p95": value["face_area_ratio"]["p95"],
                "edge_length_p05": value["edge_length_ratio"]["p05"],
                "edge_length_p95": value["edge_length_ratio"]["p95"],
            }
            for name, value in pose["regions"].items()
        },
    }


def build_cross_run_comparison(
    baseline: Path, candidate: Path, output: Path
) -> None:
    baseline_report = load_json(
        baseline / "reports" / "validation_report.json"
    )
    candidate_report = load_json(
        candidate / "reports" / "validation_report.json"
    )
    baseline_board = baseline / "evidence" / "pose_contact_sheet.png"
    candidate_board = candidate / "evidence" / "pose_contact_sheet.png"
    left = fit_image(baseline_board, (1050, 1400))
    right = fit_image(candidate_board, (1050, 1400))
    board = Image.new("RGB", (2140, 1500), (12, 18, 29))
    draw = ImageDraw.Draw(board)
    draw.text((25, 18), "Cross-run G40 comparison", font=FONT_TITLE, fill=(238, 242, 247))
    draw.text((25, 68), "Baseline", font=FONT_HEADING, fill=(190, 207, 226))
    draw.text((1095, 68), "Candidate", font=FONT_HEADING, fill=(190, 207, 226))
    board.paste(left, (20, 100))
    board.paste(right, (1070, 100))
    output.parent.mkdir(parents=True, exist_ok=True)
    board.save(output, optimize=True)

    shared = sorted(
        set(baseline_report["poses"]) & set(candidate_report["poses"])
    )
    comparison = {
        "schema_version": "1.0.0",
        "diagnostic_only": True,
        "baseline": {
            "root": baseline.as_posix(),
            "candidate": baseline_report["candidate"],
        },
        "candidate": {
            "root": candidate.as_posix(),
            "candidate": candidate_report["candidate"],
        },
        "shared_pose_metrics": {
            name: {
                "baseline": compact_pose_metrics(
                    baseline_report["poses"][name]
                ),
                "candidate": compact_pose_metrics(
                    candidate_report["poses"][name]
                ),
            }
            for name in shared
        },
        "board": output.as_posix(),
        "notice": "This comparison is diagnostic evidence, not approval.",
    }
    output.with_suffix(".json").write_text(
        json.dumps(comparison, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"board": output.as_posix(), "poses": shared}))


def build_manifest(run: Path) -> None:
    manifest_path = run / "reports" / "hash_manifest.json"
    files = []
    total_bytes = 0
    for path in sorted(run.rglob("*")):
        if (
            not path.is_file()
            or path == manifest_path
            or path == run / "logs" / "manifest.log"
            or path.suffix.lower() not in SUPPORTED_HASH_SUFFIXES
        ):
            continue
        size = path.stat().st_size
        total_bytes += size
        files.append(
            {
                "path": path.relative_to(run).as_posix(),
                "bytes": size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "schema_version": "1.0.0",
        "root": run.as_posix(),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "blend_checkpoint_count": sum(
            item["path"].endswith(".blend") for item in files
        ),
        "files": files,
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifest": manifest_path.as_posix(),
                "file_count": len(files),
                "total_bytes": total_bytes,
            },
            sort_keys=True,
        )
    )


def verify_run(run: Path) -> None:
    report = load_json(run / "reports" / "validation_report.json")
    invocation = load_json(run / "run_inputs" / "invocation.json")
    manifest = load_json(run / "reports" / "hash_manifest.json")
    failures = []

    if invocation["input_sha256"] != invocation["exact_copy_sha256"]:
        failures.append("exact input copy SHA-256 does not match source")
    exact_copy = Path(report["checkpoints"]["exact_input"])
    if not exact_copy.is_file() or sha256(exact_copy) != invocation["input_sha256"]:
        failures.append("exact input checkpoint is missing or has changed")

    checkpoint_paths = list(report["checkpoints"].values()) + [
        pose["stage"] for pose in report["poses"].values()
    ]
    for value in checkpoint_paths:
        if not Path(value).is_file():
            failures.append(f"missing checkpoint: {value}")
    for pose_name, pose in report["poses"].items():
        for view_name, value in pose["renders"].items():
            if not Path(value).is_file():
                failures.append(
                    f"missing render: {pose_name}/{view_name}: {value}"
                )

    weight_stats = report["weights"]["bounded_cleanup"]["stats"]
    configured_maximum = weight_stats["influences"]["configured_maximum"]
    if weight_stats["influences"]["maximum"] > configured_maximum:
        failures.append("bounded weights exceed configured influence maximum")
    if weight_stats["unweighted_vertex_count"]:
        failures.append("bounded weights contain unweighted vertices")

    for item in manifest["files"]:
        path = run / item["path"]
        if not path.is_file():
            failures.append(f"manifest entry missing: {item['path']}")
            continue
        if path.stat().st_size != item["bytes"]:
            failures.append(f"manifest size mismatch: {item['path']}")
        if sha256(path) != item["sha256"]:
            failures.append(f"manifest hash mismatch: {item['path']}")

    expected_boards = [
        run / "evidence" / "pose_contact_sheet.png",
        run / "evidence" / "neutral_vs_poses.png",
    ]
    for path in expected_boards:
        if not path.is_file():
            failures.append(f"missing evidence board: {path}")

    payload = {
        "run": run.as_posix(),
        "verified": not failures,
        "file_hashes_checked": len(manifest["files"]),
        "blend_checkpoints": len(
            {Path(value).resolve() for value in checkpoint_paths}
        ),
        "pose_count": len(report["poses"]),
        "max_influences": configured_maximum,
        "failures": failures,
    }
    print(json.dumps(payload, sort_keys=True))
    if failures:
        raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    boards = commands.add_parser("boards")
    boards.add_argument("--run", required=True, type=Path)
    manifest = commands.add_parser("manifest")
    manifest.add_argument("--run", required=True, type=Path)
    compare = commands.add_parser("compare")
    compare.add_argument("--baseline", required=True, type=Path)
    compare.add_argument("--candidate", required=True, type=Path)
    compare.add_argument("--output", required=True, type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("--run", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "boards":
        build_boards(args.run.expanduser().resolve())
    elif args.command == "manifest":
        build_manifest(args.run.expanduser().resolve())
    elif args.command == "compare":
        build_cross_run_comparison(
            args.baseline.expanduser().resolve(),
            args.candidate.expanduser().resolve(),
            args.output.expanduser().resolve(),
        )
    elif args.command == "verify":
        verify_run(args.run.expanduser().resolve())


if __name__ == "__main__":
    main()
