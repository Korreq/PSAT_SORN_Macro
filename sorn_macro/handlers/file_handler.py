from pathlib import Path 

from utilities.time_manager import TimeManager

class FileHandler:
    """Utility class for file operations like deleting files, directory and file creation."""

    @staticmethod
    def delete_files_from_directory(directory: str | Path, substring: str) -> None:
        """Delete files containing `substring` in their name, silently skipping errors."""
        dir_path = Path(directory)
        for file in dir_path.glob(f"*{substring}*"):
            try:
                if file.name != "tmp.pfb":
                    file.unlink()
            except Exception:
                # skip if file can't be deleted
                pass

    @staticmethod
    def create_directory(base_path: str | Path, name: str = "", add_timestamp: bool = False) -> Path:
        """Create a directory at base_path/name. Skip silently if creation fails."""
        base = Path(base_path)
        if not name:
            return base

        if add_timestamp:
            dir_name = f"{TimeManager.get_current_utc_time()}_{name}"
        else:
            dir_name = name

        target = base / dir_name
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception:
            # return base path on failure
            return base
        
        return target
    
    @staticmethod
    def create_info_file(file_path: str | Path, text: str) -> None:
        """Write text to file_path and skip on error."""
        path = Path(file_path)
        try:
            path.write_text(text)
        except Exception:
            # skip on failure
            pass

    @staticmethod
    def find_file_in_directory(directory: str | Path, fileName: str):
        """Find first file with matching name within `directory`."""
        found_files = []
        dir_path = Path(directory)
        epc_filename = fileName if fileName.endswith('.epc') else fileName.split('.')[0] + '.epc'
        for file in dir_path.glob(f"{epc_filename}"):
            found_files.append( str(file) )
        
        found_files.sort()
        return found_files[0] if found_files else None