
from pathlib import Path

from aia.core.filesystem.models import (
    PermissionLevel,
    FileInfo,
    ContentMatch,
)
from aia.core.filesystem.permissions import PermissionManager
from aia.core.filesystem.operations import FilesystemOperations


class FilesystemService:

    def __init__(
        self,
        permissions: PermissionManager,
        operations: FilesystemOperations
    ):
        self._permissions = permissions
        self._operations = operations

    def list_directory(self, path: Path) -> list[FileInfo]:
        if not self._permissions.check(path, PermissionLevel.READ):
            raise PermissionError(f"Read permission denied for {path}.")

        return self._operations.list_directory(path)


    def read_file(self, path: Path) -> str:
        if not self._permissions.check(path, PermissionLevel.READ):
            raise PermissionError(f"Read permission denied for {path}.")

        return self._operations.read_file(path)


    def search_files(self, path: Path, pattern: str) -> list[FileInfo]:
        if not self._permissions.check(path, PermissionLevel.READ):
            raise PermissionError(f"Read permission denied for {path}.")

        results = self._operations.search_files(path, pattern)

        return [
            item for item in results
            if self._permissions.check(item.path, PermissionLevel.READ)
        ]


    def search_content(self, path: Path, query: str) -> list[ContentMatch]:
        if not self._permissions.check(path, PermissionLevel.READ):
            raise PermissionError(f"Read permission denied for {path}.")

        if not query.strip():
            raise ValueError("Content to search cannot be an empty string.")

        files = self._operations.search_files(path, "*")

        matches: list[ContentMatch] = []

        for item in files:
            if item.is_directory:
                continue

            if not self._permissions.check(item.path, PermissionLevel.READ):
                continue

            try:
                content = self._operations.read_file(item.path)
            except UnicodeDecodeError:
                continue

            for line_number, line in enumerate(content.splitlines(), start=1):
                if query.casefold() in line.casefold():
                    matches.append(
                        ContentMatch(
                            path=item.path,
                            line_number=line_number,
                            line_content=line
                        )
                    )

        return matches


    def create_file(self, path: Path):
        if not self._permissions.check(path, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {path}.")

        self._operations.create_file(path)


    def create_directory(self, path: Path):
        if not self._permissions.check(path, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {path}.")

        self._operations.create_directory(path)


    def delete_file(self, path: Path):
        if not self._permissions.check(path, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {path}.")

        self._operations.delete_file(path)


    def delete_directory(self, path: Path):
        if not self._permissions.check(path, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {path}.")

        self._operations.delete_directory(path)


    def write_file(self, path: Path, content: str):
        if not self._permissions.check(path, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {path}.")

        self._operations.write_file(path, content)


    def move(self, source: Path, destination: Path):
        if not self._permissions.check(source, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {source}.")

        if not self._permissions.check(destination, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {destination}.")

        self._operations.move(source, destination)


    def rename(self, source: Path, new_name: str):
        if not self._permissions.check(source, PermissionLevel.WRITE):
            raise PermissionError(f"Write permission denied to {source}.")

        self._operations.rename(source, new_name)