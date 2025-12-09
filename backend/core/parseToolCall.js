export function parseToolCall(text) {
  const match = text.match(/^CALL_TOOL\s+(\w+)\s+(.*)$/);
  if (!match) return null;

  const [, tool, argsJson] = match;
  return {
    tool,
    args: JSON.parse(argsJson),
  };
}