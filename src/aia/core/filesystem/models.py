from enum import Enum
from pydantic import BaseModel
from pathlib import Path


class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"


class DirectoryPermission(BaseModel):
    path: Path
    permissions: set[PermissionLevel]


class FileInfo(BaseModel):
    name: str
    path: Path
    is_directory: bool
    size: int | None = None


class ContentMatch(BaseModel):
    path: Path
    line_number: int
    line_content: str