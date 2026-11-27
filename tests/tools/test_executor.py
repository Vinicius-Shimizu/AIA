from aia.core.tools.executor import ToolExecutor
from aia.core.tools.registry import ToolRegistry
from aia.core.tools.models import Tool
from pydantic import BaseModel, ValidationError
import pytest

class ExampleArgs(BaseModel):
    value: str

execution_log = []

def example_function(value: str):
    execution_log.append(value)
    return value


def create_tool(name: str = "example") -> Tool:
    return Tool(
        name=name,
        description="An example tool.",
        args_schema=ExampleArgs,
        function=example_function,
    )


def test_valid_args_execution():
    registry = ToolRegistry()
    tool = create_tool()

    registry.register(tool)

    executor = ToolExecutor(registry)
    assert executor.execute("example", {"value": "test"}) == "test"


def test_invalid_args_execution():
    registry = ToolRegistry()
    tool = create_tool()

    registry.register(tool)

    executor = ToolExecutor(registry)
    with pytest.raises(ValidationError):
        executor.execute("example", {"value": 1})


def test_missing_args_execution():
    registry = ToolRegistry()
    tool = create_tool()

    registry.register(tool)

    executor = ToolExecutor(registry)
    with pytest.raises(ValidationError):
        executor.execute("example", {})


def test_function_with_no_args():
    execution_log.clear()

    registry = ToolRegistry()
    tool = create_tool()

    registry.register(tool)

    executor = ToolExecutor(registry)

    with pytest.raises(ValidationError):
        executor.execute("example", {})

    assert len(execution_log) == 0