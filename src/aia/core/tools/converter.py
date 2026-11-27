from aia.core.tools.models import Tool

class ToolConverter():
    def __init__(self):
        self.converters = {
            "ollama": self.to_ollama 
        }


    def convert(self, provider: str, tool: Tool):
        return self.converters[provider](tool)

    
    def to_ollama(self, tool: Tool):
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.model_json_schema()
            }
        }


    def convert_tools(self, provider: str, tools: list[Tool]):
        converted_tools = []
        for tool in tools:
            converted_tools.append(self.convert(provider, tool))

        return converted_tools