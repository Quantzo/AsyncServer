import asyncio
from typing import List
from router import Router
from service import Service

ERROR_MESSAGE = "Service not found"

ServiceList = List[Service]

class Server:    
    def __init__(self, adress: str, port: int, routerImp: Router, services: ServiceList=[]):
        self.__loop = asyncio.get_event_loop()
        self.__adress = adress
        self.__port = port
        self.__router = routerImp
        self.__services = services
        for service in self.__services:
            service.set_loop(self.__loop)

    def start(self)->None:
        coro = asyncio.start_server(self.handle_client_connection, self.__adress, self.__port, loop=self.__loop)
        server = self.__loop.run_until_complete(coro)
        self.__loop.run_forever()

    def add_service(self, serviceImpl: Service)->None:
        self.__services.append(serviceImpl)

    def remove_service(self, name: str)->None:
        self.__services = list(filter(lambda s: s.get_service_name() != name, self.__services))

    async def handle_client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        service_name = self.__router.determine_service(reader, writer)
        responsible_services = list(filter(lambda s: s.get_service_name() == service_name, self.__services))
        if len(responsible_services) != 0:
            for service in responsible_services:
                await service.client_connected(reader, writer)
        else:
            writer.write(ERROR_MESSAGE)
            writer.write_eof()
            await writer.drain()
            writer.close()
