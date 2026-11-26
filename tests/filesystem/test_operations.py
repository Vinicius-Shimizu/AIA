from pathlib import Path

import pytest

from aia.core.filesystem.operations import FilesystemOperations

def test_directory_with_content(tmp_path: Path):
    operator = FilesystemOperations()

    child_folder = tmp_path / "child_folder"
    child_folder.mkdir()

    child_file_txt = tmp_path / "child_file.txt"
    child_file_txt.write_text("Hello")

    child_file_csv = tmp_path / "child_file.csv"
    child_file_csv.write_text("name,age")

    result = operator.list_directory(tmp_path)

    assert len(result) == 3

    files = {item.name: item for item in result}

    assert files["child_folder"].is_directory
    assert files["child_folder"].size == 0

    assert not files["child_file.txt"].is_directory
    assert files["child_file.txt"].size == 5

    assert not files["child_file.csv"].is_directory
    assert files["child_file.csv"].size == 8


def test_empty_directory(tmp_path: Path):
    operator = FilesystemOperations()

    result = operator.list_directory(tmp_path)

    assert result == []


def test_nonexistent_directory(tmp_path: Path):
    operator = FilesystemOperations()

    with pytest.raises(NotADirectoryError):
        operator.list_directory(tmp_path / "test")


def test_file_instead_of_directory(tmp_path: Path):
    operator = FilesystemOperations()

    child_file_txt = tmp_path / "child_file.txt"
    child_file_txt.write_text("Hello")

    with pytest.raises(NotADirectoryError):
        operator.list_directory(child_file_txt)


def test_read_file(tmp_path: Path):
    operator = FilesystemOperations()

    child_file_txt = tmp_path / "child_file.txt"
    child_file_txt.write_text("Hello")

    text = operator.read_file(child_file_txt)
    assert text == "Hello"


def test_read_empty_file(tmp_path: Path):
    operator = FilesystemOperations()

    child_file_txt = tmp_path / "child_file.txt"
    child_file_txt.touch()

    text = operator.read_file(child_file_txt)
    assert text == ""


def test_read_nonexistent_file(tmp_path: Path):
    operator = FilesystemOperations()

    child_file_txt = tmp_path / "child_file.txt"

    with pytest.raises(FileNotFoundError):
        operator.read_file(child_file_txt)


def test_read_directory(tmp_path: Path):
    operator = FilesystemOperations()

    with pytest.raises(IsADirectoryError):
        operator.read_file(tmp_path)


def test_search_files_by_pattern(tmp_path: Path):
    operator = FilesystemOperations()

    (tmp_path / "main.py").write_text("print('Hello')")
    (tmp_path / "utils.py").write_text("print('Utils')")
    (tmp_path / "readme.txt").write_text("Documentation")

    result = operator.search_files(tmp_path, "*.py")

    assert len(result) == 2
    assert {file.name for file in result} == {"main.py", "utils.py"}


def test_search_files_recursively(tmp_path: Path):
    operator = FilesystemOperations()

    subdirectory = tmp_path / "src" / "utils"
    subdirectory.mkdir(parents=True)

    (tmp_path / "main.py").write_text("main")
    (tmp_path / "src" / "app.py").write_text("app")
    (subdirectory / "helpers.py").write_text("helpers")

    result = operator.search_files(tmp_path, "*.py")

    assert len(result) == 3
    assert {file.name for file in result} == {
        "main.py",
        "app.py",
        "helpers.py"
    }



def test_search_files_case_insensitive(tmp_path: Path):
    operator = FilesystemOperations()

    (tmp_path / "EXAMPLE.PY").write_text("example")
    (tmp_path / "main.py").write_text("main")

    result = operator.search_files(tmp_path, "*.py")

    assert len(result) == 2
    assert {file.name for file in result} == {
        "EXAMPLE.PY",
        "main.py"
    }


def test_search_files_no_results(tmp_path: Path):
    operator = FilesystemOperations()

    (tmp_path / "readme.txt").write_text("Documentation")

    result = operator.search_files(tmp_path, "*.py")

    assert result == []


def test_search_files_nonexistent_directory(tmp_path: Path):
    operator = FilesystemOperations()

    with pytest.raises(NotADirectoryError):
        operator.search_files(tmp_path / "nonexistent", "*.py")


def test_search_content(tmp_path: Path):
    operator = FilesystemOperations()

    (tmp_path / "first.py").write_text(
        "class PermissionManager:\n    pass"
    )
    (tmp_path / "second.py").write_text(
        "def check():\n    return True"
    )

    result = operator.search_content(tmp_path, "PermissionManager")

    assert len(result) == 1
    assert result[0].path.name == "first.py"
    assert result[0].line_number == 1
    assert result[0].line_content == "class PermissionManager:"


def test_search_content_recursively(tmp_path: Path):
    operator = FilesystemOperations()

    subdirectory = tmp_path / "src"
    subdirectory.mkdir()

    (tmp_path / "main.py").write_text("class AIA:")
    (subdirectory / "utils.py").write_text("class PermissionManager:")

    result = operator.search_content(tmp_path, "class")

    assert len(result) == 2


def test_search_content_case_insensitive(tmp_path: Path):
    operator = FilesystemOperations()

    (tmp_path / "example.py").write_text("class PERMISSIONMANAGER:")

    result = operator.search_content(tmp_path, "permissionmanager")

    assert len(result) == 1


def test_search_content_no_results(tmp_path: Path):
    operator = FilesystemOperations()

    (tmp_path / "example.py").write_text("class AIA:")

    result = operator.search_content(tmp_path, "PermissionManager")

    assert result == []


def test_search_content_nonexistent_directory(tmp_path: Path):
    operator = FilesystemOperations()

    with pytest.raises(NotADirectoryError):
        operator.search_content(tmp_path / "nonexistent", "AIA")



def test_create_file(tmp_path):
    file_path = tmp_path / "new_file.txt"

    operations = FilesystemOperations()
    operations.create_file(file_path)

    assert file_path.exists()
    assert file_path.is_file()
    assert file_path.read_text() == ""


def test_create_file_already_exists(tmp_path):
    file_path = tmp_path / "existing_file.txt"
    file_path.write_text("existing content")

    operations = FilesystemOperations()

    with pytest.raises(FileExistsError):
        operations.create_file(file_path)


def test_create_file_parent_directory_does_not_exist(tmp_path):
    file_path = tmp_path / "missing" / "new_file.txt"

    operations = FilesystemOperations()

    with pytest.raises(FileNotFoundError):
        operations.create_file(file_path)


def test_create_directory(tmp_path):
    directory_path = tmp_path / "new_directory"

    operations = FilesystemOperations()
    operations.create_directory(directory_path)

    assert directory_path.exists()
    assert directory_path.is_dir()


def test_create_directory_already_exists(tmp_path):
    directory_path = tmp_path / "existing_directory"
    directory_path.mkdir()

    operations = FilesystemOperations()

    with pytest.raises(FileExistsError):
        operations.create_directory(directory_path)


def test_create_directory_parent_does_not_exist(tmp_path):
    directory_path = tmp_path / "missing" / "new_directory"

    operations = FilesystemOperations()

    with pytest.raises(FileNotFoundError):
        operations.create_directory(directory_path)


def test_delete_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")

    operations = FilesystemOperations()
    operations.delete_file(file_path)

    assert not file_path.exists()


def test_delete_file_does_not_exist(tmp_path):
    file_path = tmp_path / "missing.txt"

    operations = FilesystemOperations()

    with pytest.raises(FileNotFoundError):
        operations.delete_file(file_path)


def test_delete_file_with_directory_path(tmp_path):
    directory_path = tmp_path / "directory"
    directory_path.mkdir()

    operations = FilesystemOperations()

    with pytest.raises(IsADirectoryError):
        operations.delete_file(directory_path)


def test_delete_directory(tmp_path):
    directory_path = tmp_path / "directory"
    directory_path.mkdir()

    operations = FilesystemOperations()
    operations.delete_directory(directory_path)

    assert not directory_path.exists()


def test_delete_directory_does_not_exist(tmp_path):
    directory_path = tmp_path / "missing"

    operations = FilesystemOperations()

    with pytest.raises(NotADirectoryError):
        operations.delete_directory(directory_path)


def test_delete_non_empty_directory(tmp_path):
    directory_path = tmp_path / "directory"
    directory_path.mkdir()

    file_path = directory_path / "file.txt"
    file_path.write_text("content")

    operations = FilesystemOperations()

    with pytest.raises(OSError):
        operations.delete_directory(directory_path)

    assert directory_path.exists()
    assert file_path.exists()


def test_write_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("old content")

    operations = FilesystemOperations()
    operations.write_file(file_path, "new content")

    assert file_path.read_text(encoding="UTF-8") == "new content"


def test_write_file_with_empty_content(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("old content")

    operations = FilesystemOperations()
    operations.write_file(file_path, "")

    assert file_path.read_text(encoding="UTF-8") == ""
    assert file_path.exists()


def test_write_file_does_not_exist(tmp_path):
    file_path = tmp_path / "missing.txt"

    operations = FilesystemOperations()

    with pytest.raises(FileNotFoundError):
        operations.write_file(file_path, "new content")


def test_write_file_with_directory_path(tmp_path):
    directory_path = tmp_path / "directory"
    directory_path.mkdir()

    operations = FilesystemOperations()

    with pytest.raises(IsADirectoryError):
        operations.write_file(directory_path, "new content")


def test_move_file(tmp_path):
    source = tmp_path / "file.txt"
    destination = tmp_path / "backup"

    source.write_text("content")
    destination.mkdir()

    operations = FilesystemOperations()
    operations.move(source, destination)

    moved_file = destination / "file.txt"

    assert not source.exists()
    assert moved_file.exists()
    assert moved_file.is_file()
    assert moved_file.read_text() == "content"


def test_move_directory(tmp_path):
    source = tmp_path / "folder"
    destination = tmp_path / "backup"

    source.mkdir()
    (source / "file.txt").write_text("content")
    destination.mkdir()

    operations = FilesystemOperations()
    operations.move(source, destination)

    moved_directory = destination / "folder"

    assert not source.exists()
    assert moved_directory.exists()
    assert moved_directory.is_dir()
    assert (moved_directory / "file.txt").exists()


def test_move_source_does_not_exist(tmp_path):
    source = tmp_path / "missing"
    destination = tmp_path / "backup"
    destination.mkdir()

    operations = FilesystemOperations()

    with pytest.raises(FileNotFoundError):
        operations.move(source, destination)


def test_move_destination_is_not_directory(tmp_path):
    source = tmp_path / "file.txt"
    destination = tmp_path / "destination.txt"

    source.write_text("content")
    destination.write_text("existing content")

    operations = FilesystemOperations()

    with pytest.raises(NotADirectoryError):
        operations.move(source, destination)

    assert source.exists()


def test_move_destination_already_contains_item(tmp_path):
    source = tmp_path / "file.txt"
    destination = tmp_path / "backup"

    source.write_text("source content")
    destination.mkdir()
    (destination / "file.txt").write_text("destination content")

    operations = FilesystemOperations()

    with pytest.raises(FileExistsError):
        operations.move(source, destination)

    assert source.exists()
    assert source.read_text() == "source content"
    assert (destination / "file.txt").read_text() == "destination content"


def test_move_directory_into_itself(tmp_path):
    source = tmp_path / "folder"
    destination = source / "subfolder"

    source.mkdir()
    destination.mkdir()

    operations = FilesystemOperations()

    with pytest.raises(ValueError, match="Cannot move a directory into itself."):
        operations.move(source, destination)

    assert source.exists()
    assert destination.exists()


def test_rename_file(tmp_path):
    source = tmp_path / "file.txt"

    source.write_text("content")

    operations = FilesystemOperations()
    operations.rename(source, "new_file.txt")

    new_path = tmp_path / "new_file.txt"

    assert not source.exists()
    assert new_path.exists()
    assert new_path.is_file()
    assert new_path.read_text() == "content"


def test_rename_destination_already_exists(tmp_path):
    source = tmp_path / "file.txt"
    destination = tmp_path / "new_file.txt"

    source.write_text("source content")
    destination.write_text("destination content")

    operations = FilesystemOperations()

    with pytest.raises(FileExistsError):
        operations.rename(source, "new_file.txt")

    assert source.exists()
    assert destination.read_text() == "destination content"


def test_rename_source_does_not_exist(tmp_path):
    source = tmp_path / "missing.txt"

    operations = FilesystemOperations()

    with pytest.raises(FileNotFoundError):
        operations.rename(source, "new_file.txt")


@pytest.mark.parametrize("new_name", ["", "folder/file.txt", "../file.txt"])
def test_rename_invalid_name(tmp_path, new_name):
    source = tmp_path / "file.txt"
    source.write_text("content")

    operations = FilesystemOperations()

    with pytest.raises(ValueError):
        operations.rename(source, new_name)

    assert source.exists()
