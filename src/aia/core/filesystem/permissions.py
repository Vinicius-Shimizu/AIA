from pathlib import Path
from .models import PermissionLevel, DirectoryPermission


class PermissionManager:

    def __init__(self):
        self._permissions: dict[Path, set[PermissionLevel]] = {}

    def grant(
        self,
        path: Path,
        permissions: set[PermissionLevel]
    ) -> None:
        full_path = path.expanduser().resolve()
        if not full_path.is_dir() and not full_path.is_file():
            raise ValueError(f"{full_path} does not exist or is not a regular file/directory.")
       
        if not permissions: 
            raise ValueError("At least one permission level must be provided: 'READ', 'WRITE', 'EXECUTE'")
        if not all(isinstance(p, PermissionLevel) for p in permissions):
            raise ValueError(f"Invalid permission level: {permissions}. Choose one of the following: 'READ', 'WRITE', 'EXECUTE'.")
        
        current_permissions = self._permissions.setdefault(full_path, set())
        current_permissions.update(permissions)


    def revoke(self, path: Path, permissions_to_revoke: set[PermissionLevel]) -> None:
        full_path = path.expanduser().resolve()
        if not full_path.is_dir() and not full_path.is_file():
            raise ValueError(f"{full_path} does not exist or is not a regular file/directory.")
        
        if not permissions_to_revoke: 
            raise ValueError("At least one permission level must be provided: 'READ', 'WRITE', 'EXECUTE'")
        if not all(isinstance(p, PermissionLevel) for p in permissions_to_revoke):
            raise ValueError(f"Invalid permission level: {permissions_to_revoke}. Choose one of the following: 'READ', 'WRITE', 'EXECUTE'.")

        if full_path not in self._permissions:
            return
        
        current_permissions = self._permissions[full_path]
        current_permissions.difference_update(permissions_to_revoke)

                
    def check(
        self,
        path: Path,
        permission: PermissionLevel
    ) -> bool:
        full_path = path.expanduser().resolve()
       
        if not isinstance(permission, PermissionLevel):
            raise ValueError(f"Invalid permission level: {permission}. Choose one of the following: 'READ', 'WRITE', 'EXECUTE'.")

        for directory in (full_path, *full_path.parents):
            if directory in self._permissions:
                return permission in self._permissions[directory]

        return False

        


        