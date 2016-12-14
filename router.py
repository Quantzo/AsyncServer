import abc
from asyncio import StreamReader, StreamWriter
class Router(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def determine_service(self, reader: StreamReader, writer: StreamWriter):
        pass