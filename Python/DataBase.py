from sshtunnel import SSHTunnelForwarder
from LIB.Types import DBProps, SSHProps
from LIB.MetaClasses import Singleton
import psycopg2
from psycopg2.extensions import connection, cursor
from contextlib import contextmanager
from typing import Optional, Generator


class DataBase(metaclass=Singleton):

    def __init__(self):
        self._instance: Optional["DataBase"] = None
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

    def __call__(self, query: str, *params: any) -> list[tuple] | None:
        return self.exec(query, *params)

    @contextmanager
    def connection(self) -> Generator[cursor, None, None]:
        if not self._cur:
            raise RuntimeError("Database not connected")
        try:
            yield self._cur
        finally:
            if self._conn:
                self._conn.commit()

    def connect(self, configDB: DBProps, configSSH: SSHProps) -> bool:
        self.close()
        try:
            self._ssh = SSHTunnelForwarder(
                (configSSH.host, int(configSSH.port)),
                ssh_username=configSSH.user,
                ssh_password=configSSH.password,
                remote_bind_address=(configDB.host, int(configDB.port)),
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
            print(f"Connection failed: {e}")
            self.close()
            return False

    def exec(self, query: str, *params: any) -> list[tuple] | None:
        with self.connection() as cur:
            cur.execute(query, params)
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return None

    def is_connected(self) -> bool:
        return all((self._ssh, self._conn, self._cur))
