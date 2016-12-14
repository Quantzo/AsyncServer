import abc
import uuid
from asyncio import StreamReader, StreamWriter, ensure_future
from typing import Tuple

ConnectionStreams = Tuple[StreamReader, StreamWriter]

class Service(metaclass=abc.ABCMeta):
    def __init__(self, name: str):
        self.__service_name = name
        self.__client_list = []
        self._loop = None

    def set_loop(self, loop):
        self._loop = loop

    def get_service_name(self)->str:
        return self.__service_name

    async def __listen_to_client(self, clientid: uuid.UUID, reader: StreamReader)->None:
        if reader != None:
            try:
                data = await reader.readline()         
                ensure_future(self.__listen_to_client(clientid, reader), loop=self._loop)
                await self.message_recived(data.decode(), clientid)
            except ConnectionResetError:
                self.client_disconnected(clientid)


    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        if reader != None:
            clientid = uuid.uuid4()
            self.__client_list.append((clientid, reader, writer))
            await self.on_client_connected(reader, writer)
            ensure_future(self.__listen_to_client(clientid, reader), loop=self._loop)
            

    def find_client_by_id(self, clientid: uuid.UUID)->ConnectionStreams:
        try:
            client = list(filter(lambda i: i[0] == clientid, self.__client_list))[0]
            return (client[1], client[2])
        except IndexError:
            raise NameError("Client not found")

    def client_disconnected(self, clientid: uuid.UUID):
        self.__client_list = list(filter(lambda i: i[0] != clientid, self.__client_list))
        print("Client disconected:")
        print(clientid)

    def client_disconnected_with_writer(self, writer: StreamWriter)->None:
        self.__client_list = list(filter(lambda i: i[2] != writer, self.__client_list))


    async def send_text_message(self, data: str,  writer : StreamWriter)->None:
        writer.write(data.encode())       
        await writer.drain()


    async def send_text_message_with_uuid(self, data: str, clientid: uuid.UUID)->None:
        connection = self.find_client_by_id(clientid)
        await self.send_text_message_with_writer(data,connection[1], clientid)

    async def send_text_message_with_writer(self, data: str, writer : StreamWriter, clientid: uuid.UUID)->None:
        try:
            await self.send_text_message(data, writer)
        except ConnectionResetError:
            self.client_disconnected(clientid)
        
    async def broadcast_text_message(self, data: str)->None:
        for client in self.__client_list:
            await self.send_text_message_with_writer(data, client[2], client[0])
    
    @abc.abstractmethod
    async def on_client_connected(self, reader: StreamReader, writer: StreamWriter)->None:
        pass
    @abc.abstractmethod
    async def message_recived(self, data: str, clientid: uuid.UUID)->None:
        pass


