import os
from LIB.Types import DBProps, SSHProps, SOAPProps
from LIB.MetaClasses import Singleton
from configparser import ConfigParser
from typing import Literal, Type, TypeVar
from dataclasses import fields

LITERAL_TO_DATACLASS = {
    "db": DBProps,
    "ssh": SSHProps,
    "soap": SOAPProps,
}

T = TypeVar("T", DBProps, SSHProps, SOAPProps)


class Config(metaclass=Singleton):
    def __init__(self, config_name: str = "config") -> None:
        self.config_file = f"{os.path.expanduser("~")}/.{config_name}.ini"
        self.config = ConfigParser()
        self.read()

    def save(self):
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

    def read(self):
        if not os.path.exists(self.config_file):
            return
        self.config.read(self.config_file)

    def _get_props(self, section: str, prop_class: Type[T]) -> T:
        self.read()
        if section not in self.config:
            return prop_class(**{f.name: "" for f in fields(prop_class)})
        return prop_class(
            **{f.name: self.config[section].get(f.name, "") for f in fields(prop_class)}
        )

    def _set_props(self, section: str, value: T):
        self.config[section] = {
            f.name: getattr(value, f.name).strip() for f in fields(value)
        }
        self.save()

    @property
    def db(self) -> DBProps:
        return self._get_props("DATABASE", DBProps)

    @db.setter
    def db(self, value: DBProps):
        self._set_props("DATABASE", value)

    @property
    def ssh(self) -> SSHProps:
        return self._get_props("SSH", SSHProps)

    @ssh.setter
    def ssh(self, value: SSHProps):
        self._set_props("SSH", value)

    @property
    def soap(self) -> SOAPProps:
        return self._get_props("SOAP", SOAPProps)

    @soap.setter
    def soap(self, value: SOAPProps):
        self._set_props("SOAP", value)

    def is_configured(
        self, config: Literal["db", "ssh", "soap", "all"] = "all"
    ) -> bool:
        props_to_check = {
            "db": [self.db],
            "ssh": [self.ssh],
            "soap": [self.soap],
            "all": [self.db, self.ssh, self.soap],
        }[config]

        return all(
            all(bool(getattr(prop, field.name)) for field in fields(prop))
            for prop in props_to_check
        )
