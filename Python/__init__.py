from LIB.CLI import CLI
from LIB.Config import Config
from LIB.DataBase import DataBase
from LIB.SOAP import SOAP
from LIB.MetaClasses import Singleton


class _LIB(metaclass=Singleton):

    def __init__(self):
        self._CLI = CLI()
        self._Config = Config()
        self._DataBase = DataBase()
        self._SOAP = SOAP()

    @property
    def CLI(self) -> CLI:
        return self._CLI

    @property
    def Config(self) -> Config:
        return self._Config

    @property
    def DataBase(self) -> DataBase:
        return self._DataBase

    @property
    def SOAP(self) -> SOAP:
        return self._SOAP


LIB = _LIB()
