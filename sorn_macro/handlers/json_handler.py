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
            
            
    def get_input_dict(self) -> Dict[str, List[dict]]:
        """Return a dictionary mapping each category to its list of full item dicts."""
        categories = ("buses", "generators", "transformers", "shunts")
        return {
            cat: self.data.get(cat, [])
            for cat in categories
        }
