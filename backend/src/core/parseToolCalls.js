export function parseToolCalls(text) {
  const calls = [];
  const lines = text.split('\n');

  for (const line of lines) {
    const match = line.trim().match(/^CALL_TOOL\s+(\w+)\s+(.*)$/);
    if (match) {
      const [, tool, argsJson] = match;
      try {
        calls.push({
          tool,
          args: JSON.parse(argsJson),
        });
      } catch (error) {
        console.error(`Failed to parse arguments for tool ${tool}:`, error);
      }
    }
  }

  return calls.length > 0 ? calls : null;
}