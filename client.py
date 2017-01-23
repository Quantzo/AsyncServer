from asyncio import open_connection, ensure_future, get_event_loop, AbstractEventLoop

def watch_stdin()->str:
    return input()

class Client:
    def __init__(self, host: str, port: int, loop: AbstractEventLoop):
        self.__host = host
        self.__port = port
        self.__reader = None
        self.__writer = None
        self.__loop = loop

    def close(self)->None:
        self.__loop.stop()

    def send_text_message(self, message: str)->None:
        self.__writer.write((message+"\n").encode())
        
    async def create_input(self):
        while True:
            message = await self.__loop.run_in_executor(None, watch_stdin)
            if message == "close()":
                self.close()
                break
            self.__loop.call_soon(self.send_text_message, message)

    async def connect(self)->None:
        reader, writer = await open_connection(self.__host, self.__port,loop = self.__loop)
        self.__reader = reader
        self.__writer = writer
        ensure_future(self.create_input())
        while not reader.at_eof():
            message = await reader.readline()
            print((message.decode()).strip())
    
def main():
    loop = get_event_loop()
    client = Client("127.0.0.1",8888, loop)
    ensure_future(client.connect())
    loop.run_forever()

if __name__ == '__main__':
    main()

