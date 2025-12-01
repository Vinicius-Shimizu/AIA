// -------------------------------
// AIA MCP Server — Safe Dynamic App Discovery + EXE Fallback
// -------------------------------
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execSync, exec } from "child_process";
import fs from "fs";
import path from "path";

// -----------------------------------------------
// MCP Server Setup
// -----------------------------------------------
const mcpServer = new McpServer({
  name: "aia-mcp",
  display_name: "AIA MCP Server",
  version: "4.0.0",
});

// -----------------------------------------------
// open_app tool
// -----------------------------------------------
mcpServer.registerTool(
  "open_app",
  {
    title: "Open application",
    description: "Opens an app using whitelist or dynamic discovery.",
    inputSchema: z.object({ app_name: z.string() }),
    outputSchema: z.object({
      result: z.boolean(),
      message: z.string(),
    }),
  },

  async ({ app_name }) => {
    const lower = app_name.toLowerCase();

    try {
      // Windows command to open Spotify
      // if (lower === "spotify") {
      //   exec(`start "" "spotify"`);  // works if registered as protocol handler
      // }
      exec(`start "" "${lower}"`);
      return { result: true, message: `Attempted to open ${app_name}` };

    } catch (err) {
      return { result: false, message: `Failed: ${err.message}` };
    }
  }
);


// -----------------------------------------------
// Start STDIO transport
// -----------------------------------------------
const transport = new StdioServerTransport();
await mcpServer.connect(transport);
// async function start() {
//   await mcpServer.connect(transport);
// }

// start();
