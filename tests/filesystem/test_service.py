from pathlib import Path

import pytest

from aia.core.filesystem.permissions import PermissionManager
from aia.core.filesystem.operations import FilesystemOperations
from aia.core.filesystem.service import FilesystemService
from aia.core.filesystem.models import PermissionLevel


def test_list_directory_with_permission(tmp_path: Path):
    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    (tmp_path / "example.py").write_text("print('Hello')")

    permissions.grant(tmp_path, {PermissionLevel.READ})

    result = service.list_directory(tmp_path)

    assert len(result) == 1
    assert result[0].name == "example.py"


def test_list_directory_without_permission(tmp_path: Path):
    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.list_directory(tmp_path)


def test_read_file_with_permission(tmp_path: Path):
    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    file_path = tmp_path / "example.py"
    file_path.write_text("print('Hello')")

    permissions.grant(file_path, {PermissionLevel.READ})

    result = service.read_file(file_path)

    assert result == "print('Hello')"


def test_read_file_without_permission(tmp_path: Path):
    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    file_path = tmp_path / "example.py"
    file_path.write_text("print('Hello')")

    with pytest.raises(PermissionError):
        service.read_file(file_path)




def test_search_files_with_permission(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hello')")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.READ})

    result = service.search_files(tmp_path, "*.py")

    assert len(result) == 1
    assert result[0].path == file_path


def test_search_files_without_permission(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hello')")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.search_files(tmp_path, "*.py")


def test_search_content_with_permission(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text(
        "print('hello')\n"
        "print('world')\n"
    )

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.READ})

    result = service.search_content(tmp_path, "hello")

    assert len(result) == 1
    assert result[0].path == file_path
    assert result[0].line_number == 1
    assert result[0].line_content == "print('hello')"


def test_search_content_without_permission(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hello')")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.search_content(tmp_path, "hello")


def test_search_files_excludes_files_without_read_permission(tmp_path):
    public_file = tmp_path / "public.py"
    secret_file = tmp_path / "secret.py"

    public_file.write_text("public content")
    secret_file.write_text("secret content")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.READ})
    permissions.grant(secret_file, {PermissionLevel.WRITE})

    result = service.search_files(tmp_path, "*.py")

    result_paths = {item.path for item in result}

    assert public_file in result_paths
    assert secret_file not in result_paths


def test_search_content_excludes_files_without_read_permission(tmp_path):
    public_file = tmp_path / "public.py"
    secret_file = tmp_path / "secret.py"

    public_file.write_text("this is public content")
    secret_file.write_text("this is secret content")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.READ})
    permissions.grant(secret_file, {PermissionLevel.WRITE})

    result = service.search_content(tmp_path, "content")

    result_paths = {match.path for match in result}

    assert public_file in result_paths
    assert secret_file not in result_paths



def test_search_content_with_empty_query(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("hello world")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.READ})

    with pytest.raises(ValueError, match="Content to search cannot be an empty string."):
        service.search_content(tmp_path, "")


def test_search_content_with_whitespace_query(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("hello world")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.READ})

    with pytest.raises(ValueError, match="Content to search cannot be an empty string."):
        service.search_content(tmp_path, "   ")


def test_search_content_with_query_containing_spaces(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text(
        "hello world\n"
        "helloworld\n"
        "hello there world\n"
    )

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.READ})

    result = service.search_content(tmp_path, "hello world")

    assert len(result) == 1
    assert result[0].path == file_path
    assert result[0].line_number == 1
    assert result[0].line_content == "hello world"



def test_create_file_with_permission(tmp_path):
    file_path = tmp_path / "new_file.txt"

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.WRITE})

    service.create_file(file_path)

    assert file_path.exists()
    assert file_path.is_file()


def test_create_file_without_permission(tmp_path):
    file_path = tmp_path / "new_file.txt"

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.create_file(file_path)

    assert not file_path.exists()



def test_create_directory_with_permission(tmp_path):
    directory_path = tmp_path / "new_directory"

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.WRITE})

    service.create_directory(directory_path)

    assert directory_path.exists()
    assert directory_path.is_dir()


def test_create_directory_without_permission(tmp_path):
    directory_path = tmp_path / "new_directory"

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.create_directory(directory_path)

    assert not directory_path.exists()



def test_delete_file_with_permission(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.WRITE})

    service.delete_file(file_path)

    assert not file_path.exists()


def test_delete_file_without_permission(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.delete_file(file_path)

    assert file_path.exists()



def test_delete_directory_with_permission(tmp_path):
    directory_path = tmp_path / "directory"
    directory_path.mkdir()

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.WRITE})

    service.delete_directory(directory_path)

    assert not directory_path.exists()


def test_delete_directory_without_permission(tmp_path):
    directory_path = tmp_path / "directory"
    directory_path.mkdir()

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.delete_directory(directory_path)

    assert directory_path.exists()


def test_write_file_with_permission(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("old content")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    permissions.grant(tmp_path, {PermissionLevel.WRITE})

    service.write_file(file_path, "new content")

    assert file_path.read_text(encoding="UTF-8") == "new content"


def test_write_file_without_permission(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("old content")

    permissions = PermissionManager()
    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.write_file(file_path, "new content")

    assert file_path.read_text(encoding="UTF-8") == "old content"


def test_move_with_permission(tmp_path):
    source = tmp_path / "file.txt"
    destination = tmp_path / "backup"

    source.write_text("content")
    destination.mkdir()

    permissions = PermissionManager()
    permissions.grant(source, {PermissionLevel.WRITE})
    permissions.grant(destination, {PermissionLevel.WRITE})

    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    service.move(source, destination)

    moved_file = destination / "file.txt"

    assert not source.exists()
    assert moved_file.exists()
    assert moved_file.read_text() == "content"


def test_move_without_source_permission(tmp_path):
    source = tmp_path / "file.txt"
    destination = tmp_path / "backup"

    source.write_text("content")
    destination.mkdir()

    permissions = PermissionManager()
    permissions.grant(destination, {PermissionLevel.WRITE})

    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError, match="Write permission denied"):
        service.move(source, destination)

    assert source.exists()


def test_move_without_destination_permission(tmp_path):
    source = tmp_path / "file.txt"
    destination = tmp_path / "backup"

    source.write_text("content")
    destination.mkdir()

    permissions = PermissionManager()
    permissions.grant(source, {PermissionLevel.WRITE})

    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError, match="Write permission denied"):
        service.move(source, destination)

    assert source.exists()


def test_rename_with_permission(tmp_path):
    source = tmp_path / "file.txt"
    source.write_text("content")

    permissions = PermissionManager()
    permissions.grant(source, {PermissionLevel.WRITE})

    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    service.rename(source, "new_file.txt")

    new_path = tmp_path / "new_file.txt"

    assert not source.exists()
    assert new_path.exists()
    assert new_path.read_text() == "content"


def test_rename_without_permission(tmp_path):
    source = tmp_path / "file.txt"
    source.write_text("content")

    permissions = PermissionManager()

    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError, match="Write permission denied"):
        service.rename(source, "new_file.txt")

    assert source.exists()
    assert not (tmp_path / "new_file.txt").exists()


def test_rename_without_permission_preserves_file(tmp_path):
    source = tmp_path / "file.txt"
    source.write_text("original content")

    permissions = PermissionManager()

    operations = FilesystemOperations()
    service = FilesystemService(permissions, operations)

    with pytest.raises(PermissionError):
        service.rename(source, "new_file.txt")

    assert source.exists()
    assert source.read_text() == "original content"
