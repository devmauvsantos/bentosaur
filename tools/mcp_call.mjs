#!/usr/bin/env node

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { extname, join, resolve } from "node:path";

const [serverName, toolName, inputPath] = process.argv.slice(2);

if (!serverName || !toolName || !inputPath) {
  console.error(
    "Usage: node tools/mcp_call.mjs <server-name> <tool-name> <input.json>",
  );
  process.exit(2);
}

const configPath = join(homedir(), ".claude.json");
const config = JSON.parse(await readFile(configPath, "utf8"));
const project = config.projects?.[process.cwd()];
const server = project?.mcpServers?.[serverName];

if (!server?.url || !server?.headers) {
  console.error(`MCP server "${serverName}" is not configured for ${process.cwd()}`);
  process.exit(2);
}

async function resolveFileDirectives(value) {
  if (Array.isArray(value)) {
    return Promise.all(value.map(resolveFileDirectives));
  }

  if (!value || typeof value !== "object") return value;

  if (Object.keys(value).length === 1 && value.$base64_file) {
    return (await readFile(resolve(value.$base64_file))).toString("base64");
  }

  if (Object.keys(value).length === 1 && value.$json_stringify) {
    return JSON.stringify(await resolveFileDirectives(value.$json_stringify));
  }

  const entries = await Promise.all(
    Object.entries(value).map(async ([key, child]) => [
      key,
      await resolveFileDirectives(child),
    ]),
  );

  return Object.fromEntries(entries);
}

function parseResponseBody(contentType, body) {
  if (!body.trim()) return [];

  if (!contentType.includes("text/event-stream")) {
    return [JSON.parse(body)];
  }

  return body
    .split(/\r?\n/)
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trim())
    .filter((line) => line && line !== "[DONE]")
    .map((line) => JSON.parse(line));
}

async function send(payload, sessionId) {
  const headers = {
    Accept: "application/json, text/event-stream",
    "Content-Type": "application/json",
    ...server.headers,
  };

  if (sessionId) headers["Mcp-Session-Id"] = sessionId;

  const response = await fetch(server.url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  const body = await response.text();

  if (!response.ok) {
    throw new Error(`MCP HTTP ${response.status}: ${body.slice(0, 500)}`);
  }

  return {
    sessionId: response.headers.get("mcp-session-id") ?? sessionId,
    messages: parseResponseBody(response.headers.get("content-type") ?? "", body),
  };
}

async function externalizeImages(result) {
  const imageDirectory = process.env.MCP_IMAGE_DIR;
  if (!imageDirectory || !Array.isArray(result?.content)) return result;

  await mkdir(resolve(imageDirectory), { recursive: true });
  let imageIndex = 0;

  const content = await Promise.all(
    result.content.map(async (item) => {
      if (item.type !== "image" || !item.data) return item;

      const subtype = item.mimeType?.split("/")[1] ?? "png";
      const extension = extname(subtype) ? subtype : `.${subtype}`;
      const filename = `${toolName}-${String(imageIndex).padStart(2, "0")}${extension}`;
      const destination = resolve(imageDirectory, filename);
      imageIndex += 1;

      await writeFile(destination, Buffer.from(item.data, "base64"));

      return {
        type: "saved_image",
        mimeType: item.mimeType ?? null,
        path: destination,
      };
    }),
  );

  return { ...result, content };
}

const input = await resolveFileDirectives(
  JSON.parse(await readFile(resolve(inputPath), "utf8")),
);

const initialized = await send({
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {
    protocolVersion: "2025-03-26",
    capabilities: {},
    clientInfo: {
      name: "bentosaur-art-pipeline",
      version: "0.1.0",
    },
  },
});

await send(
  {
    jsonrpc: "2.0",
    method: "notifications/initialized",
  },
  initialized.sessionId,
);

const called = await send(
  {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: {
      name: toolName,
      arguments: input,
    },
  },
  initialized.sessionId,
);

const response = called.messages.find((message) => message.id === 2);

if (!response) {
  throw new Error(`MCP tool "${toolName}" returned no response`);
}

if (response.error) {
  throw new Error(JSON.stringify(response.error));
}

console.log(
  JSON.stringify(
    {
      server: serverName,
      tool: toolName,
      result: await externalizeImages(response.result),
    },
    null,
    2,
  ),
);
