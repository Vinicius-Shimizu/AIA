from pathlib import Path
from aia.core.filesystem.models import FileInfo, ContentMatch

class FilesystemOperations:

    def list_directory(self, path: Path) -> list[FileInfo]:
        full_path = path.expanduser().resolve()
        
        if not full_path.is_dir():
            raise NotADirectoryError(f"{full_path} does not exist or is not a regular directory.")
        
        content = []
        for child in full_path.iterdir():
            is_dir = child.is_dir()
            file = FileInfo(name = child.name, 
                            path=child,
                            is_directory=is_dir,
                            size= 0 if is_dir else child.stat().st_size)
            content.append(file)
        
        return content
        

    def read_file(self, path: Path) -> str:
        full_path = path.expanduser().resolve()
        
        if full_path.is_dir():
            raise IsADirectoryError(f"{full_path} is a directory.")

        if not full_path.is_file():
            raise FileNotFoundError(f"{full_path} does not exist or is not a regular file.")

        file_content = full_path.read_text(encoding="UTF-8")
        return file_content
        

    def search_files(
        self,
        path: Path,
        pattern: str
    ) -> list[FileInfo]:
        full_path = path.expanduser().resolve()
        
        if not full_path.is_dir():
            raise NotADirectoryError(f"{full_path} does not exist or is not a regular directory.")
        
        results = []
        for child in full_path.rglob(pattern, case_sensitive=False):
            is_dir = child.is_dir()
            file = FileInfo(
                name = child.name,
                path = child,
                is_directory=is_dir,
                size = 0 if is_dir else child.stat().st_size
            )
            results.append(file)

        return results


    def search_content(
        self,
        path: Path,
        query: str
    ) -> list[ContentMatch]:
        full_path = path.expanduser().resolve()
        
        if not full_path.is_dir():
            raise NotADirectoryError(f"{full_path} does not exist or is not a regular directory.")

        matches = []
        children = self.list_directory(full_path)
        for child in children:
            if child.path.is_dir():
                matches.extend(self.search_content(child.path, query))
            else:
                try:
                    content = self.read_file(child.path)
                except UnicodeDecodeError:
                    continue

                for line_number, line in enumerate(content.splitlines(), start=1):
                    if query.casefold() in line.casefold():
                        matches.append(
                            ContentMatch(
                                path=child.path,
                                line_number=line_number,
                                line_content=line
                            )
                        )

        return matches


    def create_file(self, path: Path):
        full_path = path.expanduser().resolve()
        
        if full_path.exists():
            raise FileExistsError(f"{full_path} already exists.")

        full_path.touch()


    def create_directory(self, path: Path):
        full_path = path.expanduser().resolve()
        
        if full_path.exists():
            raise FileExistsError(f"{full_path} already exists.")

        full_path.mkdir(parents=False)


    def delete_file(self, path: Path):
        full_path = path.expanduser().resolve()
        
        if full_path.is_dir():
            raise IsADirectoryError(f"{full_path} is a directory.")

        if not full_path.is_file():
            raise FileNotFoundError(f"{full_path} does not exist or is not a regular file.")

        full_path.unlink()


    def delete_directory(self, path: Path):
        full_path = path.expanduser().resolve()
        
        if not full_path.is_dir():
            raise NotADirectoryError(f"{full_path} is not a directory.")

        if any(full_path.iterdir()):
            raise OSError(f"{full_path} must be an empty directory.")

        full_path.rmdir()


    def write_file(self, path: Path, content: str):
        full_path = path.expanduser().resolve()

        if full_path.is_dir():
            raise IsADirectoryError(f"{full_path} is a directory.")

        if not full_path.is_file():
            raise FileNotFoundError(f"{full_path} does not exist or is not a regular file.")

        full_path.write_text(content, encoding="UTF-8")


    def move(self, source: Path, destination: Path):
        full_source_path = source.expanduser().resolve()
        full_destination_path = destination.expanduser().resolve()

        if not full_source_path.exists():
            raise FileNotFoundError(f"{full_source_path} does not exist.")
        
        if not full_destination_path.is_dir():
            raise NotADirectoryError(f"{full_destination_path} is not a directory.")

        if full_destination_path.is_relative_to(full_source_path):
            raise ValueError("Cannot move a directory into itself.")
        
        final_destination = full_destination_path / full_source_path.name
        
        if final_destination.exists():
            raise FileExistsError(
                f"{final_destination} already exists."
            )

        full_source_path.rename(final_destination)


    def rename(self, source: Path, new_name: str):
        full_source_path = source.expanduser().resolve()

        if not full_source_path.exists():
            raise FileNotFoundError(f"{full_source_path} does not exist.")

        if not new_name or Path(new_name).name != new_name:
            raise ValueError("new_name must be a valid filename.")

        new_path = full_source_path.with_name(new_name)
        if new_path.exists():
            raise FileExistsError(f"{new_path} already exists.")
        
        full_source_path.rename(new_path)
        