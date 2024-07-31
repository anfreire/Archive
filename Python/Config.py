import os
from typing import Dict, Optional
from MetaClasses import Singleton
from configparser import ConfigParser


class Config(metaclass=Singleton):
    def __init__(self, file_name: str = "config") -> None:
        self.config_file = os.path.join(os.path.expanduser("~"), f".{file_name}.ini")
        self.config = ConfigParser()
        self.read()

    def save(self) -> None:
        try:
            with open(self.config_file, "w") as configfile:
                self.config.write(configfile)
        except IOError as e:
            raise IOError(f"Error saving config file: {e}")

    def read(self) -> None:
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
            except ConfigParser.Error as e:
                raise ValueError(f"Error reading config file: {e}")

    def __getitem__(self, key: str) -> Optional[Dict[str, str]]:
        return self.config[key] if key in self.config else None

    def __setitem__(self, key: str, value: Dict[str, str]) -> None:
        self.config[key] = value
        self.save()

    def get(
        self, section: str, option: str, fallback: Optional[str] = None
    ) -> Optional[str]:
        return self.config.get(section, option, fallback=fallback)

    def set(self, section: str, option: str, value: str) -> None:
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = value
        self.save()
