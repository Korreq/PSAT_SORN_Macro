import json
from pathlib import Path
from typing import Dict, List

class JsonHandler:
    """Load JSON and return a dict of sorted names per element type."""

    def __init__(self, input_file: str):
        path = Path(input_file)
        if not path.exists():
            raise FileNotFoundError(f"{input_file} not found")
        with path.open() as f:
            self.data = json.load(f)
            
    def get_input_dict(self) -> Dict[str, List[str]]:
        """
        Return a dictionary mapping each category to a sorted list of 'name' values.
        Categories: buses, transformers, generators, shunts.
        """
        categories = ("buses", "transformers", "generators", "shunts")
        return {
            cat: sorted(
                item["name"]
                for item in self.data.get(cat, [])
                if "name" in item
            )
            for cat in categories
        }
