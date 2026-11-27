from aia.core.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self._registry = registry

    def execute(self, name: str, arguments: dict):
        tool = self._registry.get(name)
        args = tool.args_schema.model_validate(arguments)
        result = tool.function(**args.model_dump())
        return result
