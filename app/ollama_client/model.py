import ollama
import json
from fastmcp import Client as MCPClient

class Model():
    def __init__(self, model: str = "qwen3:4b", mcp_instance = None):
        self.model = model
        self.mcp = mcp_instance
        self.mcp_tools = None

    @classmethod
    async def create(cls, model: str = "qwen3:4b", mcp_instance = None):
        self = cls(model, mcp_instance)
        self.mcp_tools = await self.loadMCPTools()
        return self
    
    async def loadMCPTools(self):
        if not self.mcp:
            return None
        
        tools_list = await self.mcp.list_tools()
        ollama_tools = []
        for tool in tools_list:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            })
        return ollama_tools

    async def executeTool(self, tool_name: str, arguments: dict):
        result = await self.mcp.call_tool(tool_name, arguments)
        return result
        
    async def handleQuery(self, query: str):
        print(f"Query: {query}")
        try:
            response = ollama.chat(
                model = self.model,
                messages = [{'role': 'user', 'content': query}],
                tools = self.mcp_tools,
                stream=False
            )
        except Exception as e:
            print("Error: ", e)
            return None
        
        if not response.get("message", {}).get("tool_calls"):
            return response["message"]["content"]
        
        # Process tool calls
        messages = [
            {"role": "user", "content": query},
            response["message"]
        ]

        for tool_call in response["message"]["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            args = tool_call["function"]["arguments"]

            # Parse if arguments are JSON string
            if isinstance(args, str):
                args = json.loads(args)

            # Execute the tool
            tool_result = await self.executeTool(tool_name, args)
            # print(f"✅ Tool result: {tool_result}\n")

            # Add tool response to conversation
            messages.append({
                "role": "tool",
                "content": json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result),
            })
        
        return ollama.chat(
            model=self.model,
            messages=messages
        )