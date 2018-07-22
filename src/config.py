from configparser import ConfigParser
from argparse import ArgumentParser


class ConfigStorage:

    def __init__(self, filepath):
        self.config = ConfigParser()
        self.config.read(filepath)

    def get_general_config(self):
        return self.config["GENERAL"]

    def get_application_config(self, provider_name: str) -> dict:
        try:
            return self.config[provider_name.upper()]
        except KeyError:
            raise ValueError("No config exists for this provider")


def get_command_line_args():
    parser = ArgumentParser()
    parser.add_argument("--config", type=str, required=True)

    return parser.parse_args()
