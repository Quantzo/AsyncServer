from asyncio import StreamReader, StreamWriter, sleep, ensure_future
from router import Router
from service import Service
import uuid


class SimpleRouter(Router):
    def determine_service(self, reader: StreamReader, writer: StreamWriter):
        return "echo_service"
class EchoService(Service):
    async def on_client_connected(self, reader: StreamReader, writer: StreamWriter)->None:
        await self.send_text_message("Hallo\n", writer)
        ensure_future(self.control_message(writer), loop=self._loop)

    async def message_recived(self, data: str, clientid: uuid.UUID)->None:
        print(data)
        await self.send_text_message_with_uuid(data, clientid)

    async def control_message(self, writer: StreamWriter)->None:
        while True:
            try:
                await self.send_text_message("Ping\n", writer)
            except ConnectionResetError:
                self.client_disconnected_with_writer(writer)
                break
            await sleep(1)
