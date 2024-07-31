from sshtunnel import SSHTunnelForwarder
from MetaClasses import Singleton
import psycopg2
from psycopg2.extensions import connection, cursor
from contextlib import contextmanager
from typing import Optional, Generator, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class DBProps:
    host: str
    port: int
    database: str
    user: str
    password: str


@dataclass
class SSHProps:
    host: str
    port: int
    user: str
    password: str


class DatabaseError(Exception):
    pass


class DataBase(metaclass=Singleton):
    def __init__(self):
        self._ssh: Optional[SSHTunnelForwarder] = None
        self._conn: Optional[connection] = None
        self._cur: Optional[cursor] = None

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if self._cur:
            self._cur.close()
        if self._conn:
            self._conn.close()
        if self._ssh:
            self._ssh.stop()
        self._cur = self._conn = self._ssh = None

    def __call__(self, query: str, *params: Any) -> Optional[List[Tuple]]:
        return self.exec(query, *params)

    @contextmanager
    def connection(self) -> Generator[cursor, None, None]:
        if not self._cur:
            raise DatabaseError("Database not connected")
        try:
            yield self._cur
            if self._conn:
                self._conn.commit()
        except Exception as e:
            if self._conn:
                self._conn.rollback()
            raise DatabaseError(f"Database operation failed: {e}")

    def connect(self, configDB: DBProps, configSSH: SSHProps) -> bool:
        self.close()
        try:
            self._ssh = SSHTunnelForwarder(
                (configSSH.host, configSSH.port),
                ssh_username=configSSH.user,
                ssh_password=configSSH.password,
                remote_bind_address=(configDB.host, configDB.port),
            )
            self._ssh.start()

            self._conn = psycopg2.connect(
                database=configDB.database,
                user=configDB.user,
                password=configDB.password,
                host=self._ssh.local_bind_host,
                port=self._ssh.local_bind_port,
            )
            self._cur = self._conn.cursor()
            return True
        except Exception as e:
            self.close()
            raise DatabaseError(f"Connection failed: {e}")

    def exec(self, query: str, *params: Any) -> Optional[List[Tuple]]:
        with self.connection() as cur:
            cur.execute(query, params)
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return None

    def is_connected(self) -> bool:
        return all((self._ssh, self._conn, self._cur))
