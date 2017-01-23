from asyncio import StreamReader, StreamWriter, sleep, ensure_future
from router import Router
from service import Service
import uuid


class SimpleRouter(Router):
    def determine_service(self, reader: StreamReader, writer: StreamWriter):
        return "echo_service"
class EchoService(Service):
    async def on_client_connected(self, reader: StreamReader, writer: StreamWriter, clientid: uuid.UUID)->None:
        await self.send_text_message("Hallo\n", writer)
        ensure_future(self.control_message(writer, clientid), loop=self._loop)

    async def message_recived(self, data: str, clientid: uuid.UUID)->None:
        print((str(clientid)+": "+data.strip()))
        # await self.send_text_message_with_uuid(data, clientid)
        await self.broadcast_text_message(str(clientid)+": "+data)

    async def control_message(self, writer: StreamWriter, clientid: uuid.UUID)->None:
        while True:
            try:
                await self.send_text_message(str(clientid)+": "+ "Ping\n", writer)
            except ConnectionResetError:
                self.client_disconnected_with_writer(writer)
                break
            await sleep(1)
