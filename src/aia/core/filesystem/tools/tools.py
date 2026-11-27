from aia.core.filesystem.service import FilesystemService
from aia.core.tools.executor import ToolExecutor
from aia.core.tools.registry import ToolRegistry
from aia.core.tools.models import Tool
from collections.abc import Callable
from pydantic import BaseModel
from aia.core.filesystem.tools.schemas import (
    ReadFileArgs, 
    ListDirectoryArgs, 
    SearchFilesArgs,
    SearchContentArgs,
    CreateFileArgs,
    CreateDirectoryArgs,
    DeleteFileArgs,
    DeleteDirectoryArgs,
    WriteFileArgs,
    MoveArgs,
    RenameArgs
)


class FileSystemTool:
    def __init__(self, service: FilesystemService):
        self.service = service
        self._tool_registry = ToolRegistry()
        self.tool_executor = ToolExecutor(self._tool_registry)
        self.register_tools()


    def create_tool(self, name: str, description: str, args_schema: type[BaseModel], function: Callable) -> Tool:
        return Tool(
            name=name,
            description=description,
            args_schema=args_schema,
            function=function,
        )


    def register_tools(self):
        tools = [
            self.create_tool("read_file", "Reads and returns the text content of a file at the specified path.", ReadFileArgs, self.service.read_file),
            self.create_tool("list_directory", "Lists the files and subdirectories contained in the specified directory, including their names, paths, types, and sizes.", ListDirectoryArgs, self.service.list_directory),
            self.create_tool("search_files", "Recursively searches for files and directories within the specified directory whose names match the given pattern. Matching is case-insensitive.", SearchFilesArgs, self.service.search_files),
            self.create_tool("search_content", "Recursively searches for text occurrences within readable files in the specified directory and its subdirectories. Returns the matching file paths, line numbers, and line contents.", SearchContentArgs, self.service.search_content),
            self.create_tool("create_file", "Creates a new empty file at the specified path. Fails if a file or directory already exists at that path.", CreateFileArgs, self.service.create_file),
            self.create_tool("create_directory", "Creates a new directory at the specified path. The parent directory must already exist, and the target path must not exist.", CreateDirectoryArgs, self.service.create_directory),
            self.create_tool("delete_file", "Permanently deletes the file at the specified path.", DeleteFileArgs, self.service.delete_file),
            self.create_tool("delete_directory", "Deletes an empty directory at the specified path. The directory must not contain any files or subdirectories.", DeleteDirectoryArgs, self.service.delete_directory),
            self.create_tool("write_file", "Writes the provided text content to an existing file, replacing its current contents.", WriteFileArgs, self.service.write_file),
            self.create_tool("move", "Moves a file or directory into the specified destination directory, preserving its original name. Fails if an item with the same name already exists at the destination.", MoveArgs, self.service.move),
            self.create_tool("rename", "Renames a file or directory to the specified new name within its current parent directory. Fails if the new name is already in use.", RenameArgs, self.service.rename),
        ]
        for tool in tools:
            self._tool_registry.register(tool)
        

    def list_tools(self) -> list[Tool]:
        return self._tool_registry.list_tools()
