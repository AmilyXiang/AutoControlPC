import json
import os

LAYOUT_DIR = os.path.dirname(__file__)

class KeyLayout:
    def __init__(self, model="8262"):
        config_file = os.path.join(LAYOUT_DIR, f"{model}.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.model = config.get("model", model)
        self.layout = {k: tuple(v) for k, v in config["layout"].items()}
