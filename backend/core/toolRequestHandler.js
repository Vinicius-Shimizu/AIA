import { parseToolCall } from "./parseToolCall.js";
import { callMCPTool } from "../mcp/mcpClient.js";
import { getOllamaResponse } from "../ollama/ollamaClient.js";

export async function handleToolRequest(request) {
  console.log("Handling tool request: ", request);
  const tool_call = parseToolCall(request);
  if (!tool_call) return null;

  const tool_result = await callMCPTool(tool_call.tool, tool_call.args);

  const followup = await getOllamaResponse([
    { role: "assistant", content: request },
    { role: "tool", content: JSON.stringify(tool_result) }
  ]);

  return { tool_call, tool_result, followup };
}