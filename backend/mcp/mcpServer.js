import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { exec } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const whitelistPath = path.join(__dirname, "apps_whitelist.json");
const whitelist = JSON.parse(fs.readFileSync(whitelistPath, "utf-8"));

function response(result, message){
  return {
    content: [
      {
        type: "text",
        text: message
      }
    ],
    result: result,
    message: message
  };
}

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
    description: "Opens an app using whitelist.",
    inputSchema: z.object({ app_name: z.string() }),
  },

  async ({ app_name }) => {
    const lower = app_name.toLowerCase();

    const allowed = whitelist.apps.some(app =>
      lower.includes(app.toLowerCase()) ||
      app.toLowerCase().includes(lower)
    );
    
    if(!allowed) return response(false, `App "${app_name}" is not included on the whitelist.`); 

    try {
      exec(`start "" "${lower}"`);
      return response(true, `Attempted to open ${app_name}`)

    } catch (err) {
      return response(false, `Failed: ${err.message}`);
    }
  }
);


// -----------------------------------------------
// allow_app tool
// -----------------------------------------------
mcpServer.registerTool(
  "allow_app",
  {
    title: "Allow application",
    description: "Add application to whitelist.",
    inputSchema: z.object({ app_name: z.string() })
  },
  
  async ({ app_name }) => {
    const lower = app_name.toLowerCase();

    try {
      whitelist.apps.push(lower);
      fs.writeFileSync(whitelistPath, JSON.stringify(whitelist));
      return response(true, `Added ${app_name} to whitelist.`);

    } catch (err) {
      return response(false, `Failed: ${err.message}`);
    }
  }
)

const transport = new StdioServerTransport();
await mcpServer.connect(transport);



