import { parseToolCall } from "./parseToolCall.js";
import { callMCPTool } from "../mcp/mcpClient.js";
import { getOllamaResponse } from "../ollama/ollamaClient.js";

export async function handleToolRequest(request, history = []) {
  const tool_call = parseToolCall(request);
  if (!tool_call) return null;

  const tool_result = await callMCPTool(tool_call.tool, tool_call.args);
  const messages = [
    ...history,
    { role: "assistant", content: request },
    { 
      role: "user", 
      content: `[System Notification] The tool execution returned: ${JSON.stringify(tool_result)}. Please inform the user of this result. If possible, suggest an action to the user.`
    }
  ]
  const followup = await getOllamaResponse(messages);

  return { tool_call, tool_result, followup, history };
}