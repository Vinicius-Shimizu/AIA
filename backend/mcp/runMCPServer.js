import { spawn } from "child_process";
import { pendingToolResolve, setMCPProcess } from "./mcpClient.js";

export async function runMCPServer() {
  const mcp = spawn("node", ["./mcp/mcpServer.js"], {
    stdio: ["pipe", "pipe", "pipe"],
  });

  setMCPProcess(mcp);

  mcp.stdout.on("data", (data) => {
    const lines = data.toString().split("\n");

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const json = JSON.parse(line);

        if (json.result && pendingToolResolve) {
          pendingToolResolve(json.result);
        }
      } catch {}
    }
  });
  console.log("MCP server started");

  mcp.stderr.on("data", (data) => {
    console.error("[MCP Error]", data.toString());
  });

  mcp.on("close", (code) => {
    console.error(`[MCP] exited with code ${code}`);
  });
}