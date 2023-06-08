import yaml
from pathlib import Path
from typing import Dict, Union


class ConfigReader:
    def __init__(self, config_rel_path: str):
        self.config_path = Path(__file__).parent.parent.joinpath(config_rel_path)

    def get_config(self) -> Dict[str, Union[str, int]]:

        with open(self.config_path) as config_file:
            config = yaml.safe_load(config_file)

        return config
