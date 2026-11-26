import express from "express";
import cors from "cors";

import { runMCPServer } from "./mcp/runMCPServer.js";
import { runSTTService } from "./stt/sttService.js";
import chatRoute from "./routes/chat.js";

const MAIN_PORT = 3000;
const app = express();

app.use(express.json());
app.use(cors());

// chat route
app.use("/chat", chatRoute);

async function main() {
  await runMCPServer(); // start MCP server
  await runSTTService(); // start STT

  app.listen(MAIN_PORT, async () => {
    console.log(`Server running on http://localhost:${MAIN_PORT}`);
  });
}

main();