from configparser import ConfigParser
from pathlib import Path
from typing import Any, Dict, Type

class IniHandler:
    """
    Load an INI file and retrieve typed values or the entire config as dicts.
    """

    def __init__(self, ini_file: str):
        path = Path(ini_file)
        if not path.exists():
            raise FileNotFoundError(f"{ini_file} not found")
        self.parser = ConfigParser()
        self.parser.read(path)

    def get(
        self,
        section: str,
        option: str,
        cast: Type = str
    ) -> Any:
        """
        Return a value from [section] option, cast to str, bool, int, or float.
        """
        cast_map: Dict[Type, Any] = {
            str: self.parser.get,
            bool: self.parser.getboolean,
            int: self.parser.getint,
            float: self.parser.getfloat,
        }

        getter = cast_map.get(cast)
        if not getter:
            raise ValueError(f"Unsupported cast type {cast!r}")
        if not self.parser.has_section(section):
            raise KeyError(f"Section {section!r} not found")
        if not self.parser.has_option(section, option):
            raise KeyError(f"Option {option!r} missing in section {section!r}")

        return getter(section, option)
 
    def get_config_file(self):
        """
        Return all sections and their options as nested dictionaries.
        """
        return self.parser