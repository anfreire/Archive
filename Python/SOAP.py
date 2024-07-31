from typing import Any, Optional, Callable
from requests import Session
from zeep import Client
from zeep.transports import Transport
from zeep.proxy import OperationProxy
import urllib3
from MetaClasses import Singleton
from functools import wraps
from dataclasses import dataclass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class SOAPProps:
    url: str
    username: str
    password: str


class SOAPError(Exception):
    pass


def ensure_connected(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self: "SOAP", *args: Any, **kwargs: Any) -> Any:
        if not self.is_authenticated():
            raise SOAPError("Not authenticated. Call connect() first.")
        return func(self, *args, **kwargs)

    return wrapper


class SOAP(metaclass=Singleton):
    def __init__(self) -> None:
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
            raise SOAPError("Authentication not completed")
        return self._auth.sessionid

    @property
    @ensure_connected
    def user(self) -> str:
        if self._auth is None:
            raise SOAPError("Authentication not completed")
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
            raise SOAPError(f"Connection failed: {e}")

    @ensure_connected
    def exec(self, funName: str, *args: Any) -> Any:
        if self._client is None:
            raise SOAPError("Client not initialized")
        try:
            return getattr(self._client.service, funName)(*args)
        except AttributeError:
            raise SOAPError(f"Function '{funName}' not found in SOAP service")
        except Exception as e:
            raise SOAPError(f"Error executing '{funName}': {e}")

    def is_authenticated(self) -> bool:
        return self._auth is not None and getattr(self._auth, "result", False)

    def close(self) -> None:
        if self._session:
            self._session.close()
        self._session = None
        self._transport = None
        self._client = None
        self._auth = None
