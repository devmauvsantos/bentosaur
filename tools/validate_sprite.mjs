#!/usr/bin/env node

import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { promisify } from "node:util";
import { resolve } from "node:path";

const execFileAsync = promisify(execFile);
const [imageArgument, paletteArgument, widthArgument = "64", heightArgument = "64"] =
  process.argv.slice(2);

if (!imageArgument || !paletteArgument) {
  console.error(
    "Usage: node tools/validate_sprite.mjs <image.png> <palette.json> [width] [height]",
  );
  process.exit(2);
}

const imagePath = resolve(imageArgument);
const palettePath = resolve(paletteArgument);
const expectedWidth = Number(widthArgument);
const expectedHeight = Number(heightArgument);
const palette = JSON.parse(await readFile(palettePath, "utf8"));
const allowedColors = new Set(
  palette.colors.map(({ hex }) => hex.slice(1).toUpperCase()),
);

const { stdout: dimensionsOutput } = await execFileAsync(
  "magick",
  [imagePath, "-format", "%w %h", "info:"],
  { maxBuffer: 1024 * 1024 },
);
const [width, height] = dimensionsOutput.trim().split(/\s+/).map(Number);

const { stdout: pixelsOutput } = await execFileAsync(
  "magick",
  [imagePath, "txt:-"],
  { maxBuffer: 16 * 1024 * 1024 },
);

const alphaValues = new Set();
const visibleColors = new Set();
const offPalette = new Set();
let minX = width;
let minY = height;
let maxX = -1;
let maxY = -1;
let visiblePixels = 0;

for (const line of pixelsOutput.split(/\r?\n/)) {
  const match = line.match(/^(\d+),(\d+):.*#([0-9A-Fa-f]{8})\b/);
  if (!match) continue;

  const x = Number(match[1]);
  const y = Number(match[2]);
  const rgba = match[3].toUpperCase();
  const rgb = rgba.slice(0, 6);
  const alpha = rgba.slice(6, 8);
  alphaValues.add(alpha);

  if (alpha === "00") continue;

  visiblePixels += 1;
  visibleColors.add(rgb);
  if (!allowedColors.has(rgb)) offPalette.add(rgb);
  minX = Math.min(minX, x);
  minY = Math.min(minY, y);
  maxX = Math.max(maxX, x);
  maxY = Math.max(maxY, y);
}

const hasVisiblePixels = visiblePixels > 0;
const boundingBox = hasVisiblePixels
  ? {
      x: minX,
      y: minY,
      width: maxX - minX + 1,
      height: maxY - minY + 1,
      padding: {
        left: minX,
        top: minY,
        right: width - maxX - 1,
        bottom: height - maxY - 1,
      },
    }
  : null;

const checks = {
  dimensions:
    width === expectedWidth && height === expectedHeight
      ? "pass"
      : "fail",
  has_visible_pixels: hasVisiblePixels ? "pass" : "fail",
  binary_alpha: [...alphaValues].every(
    (alpha) => alpha === "00" || alpha === "FF",
  )
    ? "pass"
    : "fail",
  palette_membership: offPalette.size === 0 ? "pass" : "fail",
  color_cap:
    visibleColors.size <= palette.maximum_colors ? "pass" : "fail",
};

const passed = Object.values(checks).every((value) => value === "pass");

console.log(
  JSON.stringify(
    {
      image: imagePath,
      expected_size: [expectedWidth, expectedHeight],
      actual_size: [width, height],
      palette: palette.id,
      checks,
      visible_pixel_count: visiblePixels,
      visible_color_count: visibleColors.size,
      alpha_levels: [...alphaValues].sort(),
      off_palette_colors: [...offPalette].sort().map((hex) => `#${hex}`),
      bounding_box: boundingBox,
      result: passed ? "pass" : "fail",
    },
    null,
    2,
  ),
);

process.exitCode = passed ? 0 : 1;
