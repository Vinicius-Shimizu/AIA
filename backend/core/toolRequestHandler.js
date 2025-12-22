import { parseToolCalls } from "./parseToolCalls.js";
import { callMCPTool } from "../mcp/mcpClient.js";
import { getOllamaResponse } from "../ollama/ollamaClient.js";
import { addToHistory, getHistory } from "./historyManager.js";

export async function handleToolRequest(request, history) {
  const tool_calls = parseToolCalls(request);
  if (!tool_calls) return null;

  const results = await Promise.all(
    tool_calls.map(async (call) => {
      const result = await callMCPTool(call.tool, call.args);
      return { tool: call.tool, ...result };
    })
  );

  const tool_message = `[System Notification] Execution results:\n${results
    .map((r) => `- Tool ${r.tool}: ${JSON.stringify(r)}`)
    .join("\n")}\nPlease inform the user and omit the tool calling command.`;
  addToHistory("user", tool_message);
  const followup = await getOllamaResponse(getHistory());

  return { tool_calls, results, followup, history };
}