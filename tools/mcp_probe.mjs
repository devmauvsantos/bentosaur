#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";

const serverName = process.argv[2];

if (!serverName) {
  console.error("Usage: node tools/mcp_probe.mjs <server-name>");
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

const tools = await send(
  {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/list",
    params: {},
  },
  initialized.sessionId,
);

const response = tools.messages.find((message) => message.id === 2);

if (!response?.result?.tools) {
  throw new Error("MCP tools/list returned no tools");
}

console.log(
  JSON.stringify(
    {
      server: serverName,
      protocolVersion:
        initialized.messages.find((message) => message.id === 1)?.result
          ?.protocolVersion ?? null,
      tools: response.result.tools,
    },
    null,
    2,
  ),
);
