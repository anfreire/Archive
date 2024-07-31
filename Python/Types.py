from dataclasses import dataclass


@dataclass
class DBProps:
    host: str
    port: str
    database: str
    user: str
    password: str


@dataclass
class SSHProps:
    host: str
    port: str
    user: str
    password: str


@dataclass
class SOAPProps:
    url: str
    username: str
    password: str
