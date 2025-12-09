import express from "express";
import cors from "cors";
import { spawn, } from "child_process";

const MAIN_PORT = 3000;
const app = express();
app.use(express.json());
app.use(cors());
let mcp = null;
let pendingToolResolve = null;

async function handleToolRequest(responseText){
  const tool_call = parseToolCall(responseText);
  if(!tool_call) return null;

  const tool_result = await callMCPTool(tool_call.tool, tool_call.args);

  const followup = await getOllamaResponse([
    { role: "assistant", content: responseText },
    { role: "tool", content: JSON.stringify(tool_result)}
  ]);

  return {tool_call, tool_result, followup};
}

async function processAIAQuery(queryArray){
  console.log("", queryArray);
  const response = await getOllamaResponse(queryArray);
  const tool_output = handleToolRequest(response);

  return {
    response,
    followup: tool_output?.followup || null,
    tool: tool_output || null
  };
}

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

async function runMCPServer() {
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
      
      for (const line of lines){
        if(!line.trim()) continue;
        
        let json;
        try{
          json = JSON.parse(line);
        } catch{
          continue;
        }
        if (json.type == "status"){
          console.log("[STT Status]:", json.text);
        }
        else if(json.type == "AIA"){
          console.log("[AIA response]:", json.text);
        }
        else if (json.type == "transcription"){
          console.log("[Command]: ", json.text);
          const  {response, followup} = await processAIAQuery([
            { role: "user", content: json.text}
          ]);

          console.log("[AIA response]: ", response);
          if (followup) console.log("[Tool followup]: ", followup);
        }
      }
    });
  })
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