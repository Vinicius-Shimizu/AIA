from pathlib import Path

import pytest

from aia.core.filesystem.permissions import PermissionManager
from aia.core.filesystem.models import PermissionLevel


def test_grant_permissions(tmp_path: Path):
    manager = PermissionManager()

    manager.grant(tmp_path, {PermissionLevel.READ, PermissionLevel.WRITE})
    
    assert manager.check(tmp_path, PermissionLevel.READ)
    assert manager.check(tmp_path, PermissionLevel.WRITE)
    assert not manager.check(tmp_path, PermissionLevel.EXECUTE)


def test_revoke_permissions(tmp_path: Path):
    manager = PermissionManager()

    manager.grant(tmp_path, {PermissionLevel.READ, PermissionLevel.WRITE})
    manager.revoke(tmp_path, {PermissionLevel.WRITE})

    assert manager.check(tmp_path, PermissionLevel.READ)
    assert not manager.check(tmp_path, PermissionLevel.WRITE)


def test_revoke_last_permission(tmp_path: Path):
    manager = PermissionManager()
    
    parent_dir = tmp_path / "parent"
    child_dir = parent_dir / "child"

    parent_dir.mkdir(parents=True)
    child_dir.mkdir(parents=True)

    manager.grant(parent_dir, {PermissionLevel.READ, PermissionLevel.WRITE})
    manager.grant(child_dir, {PermissionLevel.READ})

    manager.revoke(child_dir, {PermissionLevel.READ})

    assert not manager.check(child_dir, PermissionLevel.READ)
    assert not manager.check(child_dir, PermissionLevel.WRITE)


def test_inherit_parent_permissions(tmp_path: Path):
    manager = PermissionManager()
    
    parent_dir = tmp_path / "parent"
    child_dir = parent_dir / "child"

    parent_dir.mkdir(parents=True)
    child_dir.mkdir(parents=True)

    manager.grant(parent_dir, {PermissionLevel.READ, PermissionLevel.WRITE})

    assert manager.check(child_dir, PermissionLevel.READ)
    assert manager.check(child_dir, PermissionLevel.WRITE)
    assert not manager.check(child_dir, PermissionLevel.EXECUTE)


def test_override_parent_permissions(tmp_path: Path):
    manager = PermissionManager()
    
    parent_dir = tmp_path / "parent"
    child_dir = parent_dir / "child"

    parent_dir.mkdir(parents=True)
    child_dir.mkdir(parents=True)

    manager.grant(parent_dir, {PermissionLevel.READ, PermissionLevel.WRITE})
    manager.grant(child_dir, {PermissionLevel.READ})

    assert manager.check(child_dir, PermissionLevel.READ)
    assert not manager.check(child_dir, PermissionLevel.WRITE)


def test_default_deny(tmp_path: Path):
    manager = PermissionManager()

    assert not manager.check(tmp_path, PermissionLevel.READ)
    assert not manager.check(tmp_path, PermissionLevel.WRITE)
    assert not manager.check(tmp_path, PermissionLevel.EXECUTE)


def test_check_invalid_permission(tmp_path: Path):
    manager = PermissionManager()

    with pytest.raises(ValueError):
        manager.check(tmp_path, "READ")


def test_check_invalid_permission_type(tmp_path: Path):
    manager = PermissionManager()

    with pytest.raises(ValueError):
        manager.check(tmp_path, 123)


def test_grant_file_permissions(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('Hello')")

    manager = PermissionManager()
    manager.grant(file_path, {PermissionLevel.READ})

    assert manager.check(file_path, PermissionLevel.READ)
    assert not manager.check(file_path, PermissionLevel.WRITE)


def test_file_inherits_parent_permissions(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('Hello')")

    manager = PermissionManager()
    manager.grant(tmp_path, {PermissionLevel.READ, PermissionLevel.WRITE})

    assert manager.check(file_path, PermissionLevel.READ)
    assert manager.check(file_path, PermissionLevel.WRITE)
    assert not manager.check(file_path, PermissionLevel.EXECUTE)


def test_file_overrides_parent_permissions(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('Hello')")

    manager = PermissionManager()
    manager.grant(tmp_path, {PermissionLevel.READ, PermissionLevel.WRITE})
    manager.grant(file_path, {PermissionLevel.READ})

    assert manager.check(file_path, PermissionLevel.READ)
    assert not manager.check(file_path, PermissionLevel.WRITE)
    assert not manager.check(file_path, PermissionLevel.EXECUTE)


def test_revoke_last_file_permission(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('Hello')")

    manager = PermissionManager()
    manager.grant(tmp_path, {PermissionLevel.READ, PermissionLevel.WRITE})
    manager.grant(file_path, {PermissionLevel.READ})
    manager.revoke(file_path, {PermissionLevel.READ})

    assert not manager.check(file_path, PermissionLevel.READ)
    assert not manager.check(file_path, PermissionLevel.WRITE)
    assert manager.check(tmp_path, PermissionLevel.READ)
    assert manager.check(tmp_path, PermissionLevel.WRITE)