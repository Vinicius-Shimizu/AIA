import { getOllamaResponse } from "../ollama/ollamaClient.js";
import { handleToolRequest } from "./toolRequestHandler.js";

export async function processAIAQuery(queryArray) {
  const response = await getOllamaResponse(queryArray);

  const tool_output = await handleToolRequest(response, queryArray);

  return {
    response,
    followup: tool_output?.followup || null,
    tool: tool_output || null,
  };
}