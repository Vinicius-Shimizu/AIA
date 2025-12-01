import express from "express";
import cors from "cors";
import { spawn, } from "child_process";

const MAIN_PORT = 3000;
const app = express();
app.use(express.json());
app.use(cors());
let mcp = null;
let pendingToolResolve = null;

function parseToolCall(text) {
  const match = text.match(/^CALL_TOOL\s+(\w+)\s+(.*)$/);
  if (!match) return null;

  const [, tool, argsJson] = match;
  return { tool, args: JSON.parse(argsJson) };
}

function callMCPTool(tool, args) {
  return new Promise((resolve) => {
    const id = Math.floor(Math.random() * 100000);

    pendingToolResolve = resolve;

    const payload = {
      jsonrpc: "2.0",
      id,
      method: "tools/call",
      params: {
        name: tool,
        arguments: args
      }
    };

    mcp.stdin.write(JSON.stringify(payload) + "\n");
  }); 
}

async function getOllamaResponse(query){
  const response = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "aia",
      messages: query,
      stream: false,
    }),
  });

  const data = await response.json();
  const assistantContent = data.message.content;
  return assistantContent;
}


async function runSTTService() {
  const stt = spawn("python", ["-u", "stt_engine.py"]);

  let buffer = "";
  await new Promise(resolve => {
    stt.stdout.on("data", async (chunk) => {
      buffer += chunk;
  
      let lines = buffer.split("\n");
      buffer = lines.pop(); // save incomplete line
  
      for (const line of lines) {
        if (!line.trim()) continue;
  
        try {
          const json = JSON.parse(line);
  
          switch (json.type) {
            case "AIA":
              console.log("[STT AIA]:", json.text);
              break;
            case "transcription":
              console.log("[STT Command]:", json.text);
              const query = [{"role": "user", "content": json.text}]
              const response = await getOllamaResponse(query);
              console.log("[AIA]: ", response); 
              const toolCall = parseToolCall(response);

              if (toolCall) {
                const result = await callMCPTool(toolCall.tool, toolCall.args);
                console.log("[MCP Result]", result);

                // send result back to Ollama as a message
                const followup = await getOllamaResponse([
                  { role: "assistant", content: response },
                  { role: "tool", content: JSON.stringify(result) }
                ]);

                console.log("[AIA Followup]: ", followup);
              } 
              break;
            case "status":
              console.log("[STT Status]:", json.text);
              resolve();
              break;
            default:
              console.log("[STT LOG]", json);
          }
  
        } catch (err) {
          console.log("[JSON PARSE ERROR]", err);
          console.log("[LINE RECEIVED]", line);
        }
      }
    });
  })
}

function runMCPServer() {
  mcp = spawn("node", ["mcp_server.js"], {
    stdio: ["pipe", "pipe", "pipe"]
  });

  mcp.stdout.on("data", (data) => {
  const lines = data.toString().split("\n");

  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const json = JSON.parse(line);
      if (json.result && pendingToolResolve) {
        pendingToolResolve(json.result);
        pendingToolResolve = null;
      }
    } catch {}
  }
  });

  mcp.stderr.on("data", (data) => {
    console.error("[MCP Error]", data.toString());
  });

  mcp.on("close", (code) => {
    console.error(`[MCP] exited with code ${code}`);
  });
}

app.post("/chat", async (req, res) => {
  try{
    const query = req.body.messages;
    console.log("Query sent: ", query);
    const response = await getOllamaResponse(query);
    res.json({message: response});
  }catch (err) {
    console.error("Error contacting Ollama:", err);
    res.status(500).json({ error: "Failed to reach Ollama." });
  }
});


async function main() {
  runMCPServer();
  app.listen(MAIN_PORT, async () => {
    console.log(`Server running on http://localhost:${MAIN_PORT}`);
    await runSTTService();
  });
}

main();