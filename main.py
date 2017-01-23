from server import Server
from simpleexample import SimpleRouter, EchoService

serv = Server('127.0.0.1',8888, SimpleRouter(), [EchoService('echo_service')])
serv.start()
    