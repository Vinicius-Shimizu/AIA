import pytest
from pydantic import BaseModel

from aia.core.tools.models import Tool
from aia.core.tools.registry import ToolRegistry


class ExampleArgs(BaseModel):
    value: str


def example_function(value: str):
    return value


def create_tool(name: str = "example") -> Tool:
    return Tool(
        name=name,
        description="An example tool.",
        args_schema=ExampleArgs,
        function=example_function,
    )


def test_register_tool():
    registry = ToolRegistry()
    tool = create_tool()

    registry.register(tool)

    assert registry.get("example") == tool


def test_register_duplicate_tool():
    registry = ToolRegistry()

    registry.register(create_tool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(create_tool())


def test_get_unregistered_tool():
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="not registered"):
        registry.get("missing")


def test_list_tools():
    registry = ToolRegistry()

    first_tool = create_tool("first")
    second_tool = create_tool("second")

    registry.register(first_tool)
    registry.register(second_tool)

    assert registry.list_tools() == [first_tool, second_tool]


def test_list_tools_empty():
    registry = ToolRegistry()

    assert registry.list_tools() == []
