#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { basename, extname, resolve } from "node:path";

function usage() {
  console.error(
    "Usage: node build_notion_visual_attachment.mjs <input-image> <output-html> [title]",
  );
}

const [, , inputArg, outputArg, titleArg] = process.argv;
if (!inputArg || !outputArg) {
  usage();
  process.exit(2);
}

const inputPath = resolve(inputArg);
const outputPath = resolve(outputArg);
const extension = extname(inputPath).toLowerCase();
const mimeTypes = new Map([
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".png", "image/png"],
  [".webp", "image/webp"],
]);
const mimeType = mimeTypes.get(extension);
if (!mimeType) {
  throw new Error(`Unsupported image extension: ${extension}`);
}

const title = titleArg || basename(inputPath);
const imageBase64 = (await readFile(inputPath)).toString("base64");
const escapedTitle = title
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapedTitle}</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; background: #101418; }
    body {
      display: grid;
      place-items: center;
      padding: 12px;
      font: 14px/1.4 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #eef6f0;
    }
    figure { width: min(100%, 1200px); margin: 0; }
    img {
      display: block;
      width: 100%;
      height: auto;
      border: 1px solid #314038;
      border-radius: 12px;
      box-shadow: 0 12px 36px rgb(0 0 0 / 35%);
    }
    figcaption { padding: 8px 4px 0; color: #b8c7be; }
  </style>
</head>
<body>
  <figure>
    <img src="data:${mimeType};base64,${imageBase64}" alt="${escapedTitle}">
    <figcaption>${escapedTitle}</figcaption>
  </figure>
</body>
</html>
`;

await writeFile(outputPath, html, "utf8");
console.log(
  JSON.stringify({
    input: inputPath,
    output: outputPath,
    source_bytes: imageBase64.length,
    output_bytes: Buffer.byteLength(html),
  }),
);
