#!/usr/bin/env python3
"""Safe launcher for the reusable G40 deformation-validation harness.

This launcher runs outside Blender. It freezes the exact input and configuration,
invokes the isolated Blender recipe, builds evidence boards, and hashes the
complete run. It never writes beside the source asset.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


HARNESS_ROOT = Path(__file__).resolve().parent
BLENDER_RECIPE = HARNESS_ROOT / "blender" / "g40_validate_in_blender.py"
ARTIFACT_TOOL = HARNESS_ROOT / "tools" / "g40_artifacts.py"
DEFAULT_BLENDER = Path("/Applications/Blender.app/Contents/MacOS/Blender")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read JSON config {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("Configuration root must be a JSON object.")
    return value


def validate_config(config: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "coordinate_contract",
        "rig",
        "weights",
        "regions",
        "poses",
        "thresholds",
        "render",
    }
    missing = sorted(required - set(config))
    if missing:
        raise SystemExit(f"Configuration is missing keys: {', '.join(missing)}")
    if config.get("diagnostic_only") is not True:
        raise SystemExit('Configuration must explicitly set "diagnostic_only": true.')
    max_influences = config["weights"].get("max_influences")
    if not isinstance(max_influences, int) or not 1 <= max_influences <= 4:
        raise SystemExit("weights.max_influences must be an integer from 1 to 4.")
    poses = config["poses"]
    if not isinstance(poses, list) or not poses:
        raise SystemExit("poses must be a non-empty JSON array.")
    names = [pose.get("name") for pose in poses]
    if len(set(names)) != len(names) or any(not name for name in names):
        raise SystemExit("Every pose needs a unique, non-empty name.")
    checkpoints = [pose.get("checkpoint") for pose in poses]
    if len(set(checkpoints)) != len(checkpoints):
        raise SystemExit("Pose checkpoint numbers must be unique.")


def ensure_safe_output(source: Path, output: Path) -> None:
    if output == source or output == source.parent:
        raise SystemExit("Output cannot be the source file or its parent directory.")
    if output in source.parents:
        raise SystemExit("Output cannot be an ancestor of the input source.")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(
            f"Refusing to overwrite non-empty run directory: {output}\n"
            "Choose a fresh output directory so prior evidence remains immutable."
        )
    output.mkdir(parents=True, exist_ok=True)


def run_logged(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("COMMAND=" + json.dumps(command) + "\n\n")
        log.flush()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            log.write(line)
        return_code = process.wait()
    if return_code:
        raise SystemExit(
            f"Command failed with exit code {return_code}. See {log_path}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a preserved, bounded G40 deformation diagnostic. This does "
            "not build or approve a production rig."
        )
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--body-object", required=True)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--blender",
        type=Path,
        default=Path(os.environ.get("G40_BLENDER", DEFAULT_BLENDER)),
    )
    parser.add_argument(
        "--compare-to",
        type=Path,
        help="Optional prior completed run for a cross-run comparison board.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.input.expanduser().resolve()
    config_path = args.config.expanduser().resolve()
    output = args.output.expanduser().resolve()
    blender = args.blender.expanduser().resolve()

    if not source.is_file() or source.suffix.lower() != ".blend":
        raise SystemExit(f"Input is not a readable .blend file: {source}")
    if not config_path.is_file():
        raise SystemExit(f"Config does not exist: {config_path}")
    if not blender.is_file():
        raise SystemExit(f"Blender executable does not exist: {blender}")
    if not BLENDER_RECIPE.is_file() or not ARTIFACT_TOOL.is_file():
        raise SystemExit("Harness installation is incomplete.")

    config = load_json(config_path)
    validate_config(config)
    ensure_safe_output(source, output)

    for directory in ("stages", "renders", "metrics", "reports", "evidence", "logs", "run_inputs"):
        (output / directory).mkdir(parents=True, exist_ok=True)

    exact_copy = output / "stages" / "00_input_exact_copy.blend"
    shutil.copy2(source, exact_copy)
    source_sha = sha256(source)
    copy_sha = sha256(exact_copy)
    if source_sha != copy_sha:
        raise SystemExit("Exact source preservation failed: SHA-256 mismatch.")

    frozen_config = output / "run_inputs" / "config.json"
    shutil.copy2(config_path, frozen_config)
    recipe_files = [Path(__file__).resolve(), BLENDER_RECIPE, ARTIFACT_TOOL]
    invocation = {
        "schema_version": "1.0.0",
        "diagnostic_only": True,
        "input": source.as_posix(),
        "input_sha256": source_sha,
        "exact_copy": exact_copy.as_posix(),
        "exact_copy_sha256": copy_sha,
        "body_object": args.body_object,
        "config_source": config_path.as_posix(),
        "config_frozen": frozen_config.as_posix(),
        "config_sha256": sha256(frozen_config),
        "blender": blender.as_posix(),
        "harness_recipes": [
            {
                "path": path.as_posix(),
                "sha256": sha256(path),
            }
            for path in recipe_files
        ],
        "compare_to": (
            args.compare_to.expanduser().resolve().as_posix()
            if args.compare_to
            else None
        ),
        "non_approval_notice": (
            "This is a bounded diagnostic rig and deformation stress harness. "
            "It does not replace production rigging, visual review, or user approval."
        ),
    }
    (output / "run_inputs" / "invocation.json").write_text(
        json.dumps(invocation, indent=2) + "\n",
        encoding="utf-8",
    )

    blender_command = [
        blender.as_posix(),
        "--background",
        source.as_posix(),
        "--python",
        BLENDER_RECIPE.as_posix(),
        "--",
        "--input",
        source.as_posix(),
        "--body-object",
        args.body_object,
        "--output",
        output.as_posix(),
        "--config",
        frozen_config.as_posix(),
    ]
    run_logged(blender_command, output / "logs" / "blender.log")

    board_command = [
        sys.executable,
        ARTIFACT_TOOL.as_posix(),
        "boards",
        "--run",
        output.as_posix(),
    ]
    run_logged(board_command, output / "logs" / "boards.log")

    if args.compare_to:
        previous = args.compare_to.expanduser().resolve()
        comparison_command = [
            sys.executable,
            ARTIFACT_TOOL.as_posix(),
            "compare",
            "--baseline",
            previous.as_posix(),
            "--candidate",
            output.as_posix(),
            "--output",
            (output / "evidence" / "cross_run_comparison.png").as_posix(),
        ]
        run_logged(
            comparison_command,
            output / "logs" / "comparison.log",
        )

    manifest_command = [
        sys.executable,
        ARTIFACT_TOOL.as_posix(),
        "manifest",
        "--run",
        output.as_posix(),
    ]
    run_logged(manifest_command, output / "logs" / "manifest.log")

    verification_command = [
        sys.executable,
        ARTIFACT_TOOL.as_posix(),
        "verify",
        "--run",
        output.as_posix(),
    ]
    subprocess.run(verification_command, check=True)

    report = load_json(output / "reports" / "validation_report.json")
    print(
        "G40_RUN_COMPLETE="
        + json.dumps(
            {
                "output": output.as_posix(),
                "diagnostic_pass": report["verdict"]["diagnostic_pass"],
                "failing_poses": report["verdict"]["failing_poses"],
                "input_sha256": source_sha,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
