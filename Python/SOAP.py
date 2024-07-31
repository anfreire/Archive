from typing import Any, Optional, Type
from requests import Session
from zeep import Client
from zeep.transports import Transport
from zeep.proxy import OperationProxy
import urllib3
from LIB.Types import SOAPProps
from LIB.MetaClasses import Singleton
from functools import wraps

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ensure_connected(func):
    @wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        if not self.is_authenticated():
            raise ConnectionError("Not authenticated. Call connect() first.")
        return func(self, *args, **kwargs)

    return wrapper


class SOAP(metaclass=Singleton):

    def __init__(self):
        self._session: Optional[Session] = None
        self._transport: Optional[Transport] = None
        self._client: Optional[Client] = None
        self._auth: Optional[OperationProxy] = None

    def __call__(self, funName: str, *args: Any) -> Any:
        return self.exec(funName, *args)

    @property
    @ensure_connected
    def sessionId(self) -> str:
        if self._auth is None:
            raise AttributeError("Authentication not completed")
        return self._auth.sessionid

    @property
    @ensure_connected
    def user(self) -> str:
        if self._auth is None:
            raise AttributeError("Authentication not completed")
        return self._auth.user

    def connect(self, config: SOAPProps) -> bool:
        try:
            self._session = Session()
            self._session.verify = False
            self._transport = Transport(session=self._session)
            self._client = Client(config.url, transport=self._transport)
            self._auth = self._client.service.userAuthentication(
                config.username,
                config.password,
            )
            return self.is_authenticated()
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    @ensure_connected
    def exec(self, funName: str, *args: Any) -> Any:
        if self._client is None:
            raise AttributeError("Client not initialized")
        return getattr(self._client.service, funName)(*args)

    def is_authenticated(self) -> bool:
        return self._auth is not None and getattr(self._auth, "result", False)
