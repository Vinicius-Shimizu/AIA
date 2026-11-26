import { getOllamaResponse } from "../ollama/ollamaClient.js";
import { handleToolRequest } from "./toolRequestHandler.js";

export async function processAIAQuery(history) {
  const response = await getOllamaResponse(history);

  const tool_output = await handleToolRequest(response, history);

  return {
    response,
    followup: tool_output?.followup || null,
    tool: tool_output || null,
  };
}