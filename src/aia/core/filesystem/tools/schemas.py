from pydantic import BaseModel
from pathlib import Path

class ReadFileArgs(BaseModel):
    path: Path


class ListDirectoryArgs(BaseModel):
    path: Path


class SearchFilesArgs(BaseModel):
    path: Path
    pattern: str


class SearchContentArgs(BaseModel):
    path: Path
    query: str


class CreateFileArgs(BaseModel):
    path: Path


class CreateDirectoryArgs(BaseModel):
    path: Path


class DeleteFileArgs(BaseModel):
    path: Path


class DeleteDirectoryArgs(BaseModel):
    path: Path


class WriteFileArgs(BaseModel):
    path: Path
    content: str


class MoveArgs(BaseModel):
    source: Path
    destination: Path


class RenameArgs(BaseModel):
    path: Path
    new_name: str
