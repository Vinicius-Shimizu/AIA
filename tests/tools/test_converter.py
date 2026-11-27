
import pytest
from pydantic import BaseModel

from aia.core.tools.models import Tool
from aia.core.tools.converter import ToolConverter


class ReadFileArgs(BaseModel):
    path: str


class WriteFileArgs(BaseModel):
    path: str
    content: str


def read_file(path: str):
    return f"Content of {path}"


def write_file(path: str, content: str):
    return None


@pytest.fixture
def converter():
    return ToolConverter()


@pytest.fixture
def read_file_tool():
    return Tool(
        name="read_file",
        description="Reads a file.",
        args_schema=ReadFileArgs,
        function=read_file,
    )


@pytest.fixture
def write_file_tool():
    return Tool(
        name="write_file",
        description="Writes content to a file.",
        args_schema=WriteFileArgs,
        function=write_file,
    )


def test_convert_ollama(converter, read_file_tool):
    result = converter.convert("ollama", read_file_tool)

    assert result["type"] == "function"
    assert result["function"]["name"] == "read_file"
    assert result["function"]["description"] == "Reads a file."
    assert result["function"]["parameters"] == ReadFileArgs.model_json_schema()


def test_convert_tools(converter, read_file_tool, write_file_tool):
    result = converter.convert_tools(
        "ollama",
        [read_file_tool, write_file_tool]
    )

    assert len(result) == 2
    assert result[0]["function"]["name"] == "read_file"
    assert result[1]["function"]["name"] == "write_file"


def test_convert_preserves_arguments_schema(converter, write_file_tool):
    result = converter.convert("ollama", write_file_tool)

    parameters = result["function"]["parameters"]

    assert parameters == WriteFileArgs.model_json_schema()
    assert "path" in parameters["properties"]
    assert "content" in parameters["properties"]
    assert set(parameters["required"]) == {"path", "content"}


def test_convert_unknown_provider(converter, read_file_tool):
    with pytest.raises(KeyError):
        converter.convert("unknown", read_file_tool)


def test_convert_tools_unknown_provider(converter, read_file_tool):
    with pytest.raises(KeyError):
        converter.convert_tools("unknown", [read_file_tool])
