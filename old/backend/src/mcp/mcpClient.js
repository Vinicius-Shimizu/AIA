let pendingToolResolve = null;
export { pendingToolResolve };

let mcp = null;
export function setMCPProcess(proc) {
  mcp = proc;
}

export function callMCPTool(tool, args) {
  return new Promise((resolve) => {
    const id = Math.floor(Math.random() * 100000);
    pendingToolResolve = resolve;

    const payload = {
      jsonrpc: "2.0",
      id,
      method: "tools/call",
      params: {
        name: tool,
        arguments: args,
      }
    };

    mcp.stdin.write(JSON.stringify(payload) + "\n");
  });
}
