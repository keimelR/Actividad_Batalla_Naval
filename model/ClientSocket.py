from model.ConnectionSocket import ConnectionSocket
import socket

class ClientSocket(ConnectionSocket):
    def __init__(
        self, 
        port = 7777, 
        address = "localhost",
        address_family: socket.AddressFamily = socket.AF_INET, 
        type: socket.SocketKind = socket.SOCK_STREAM,
        socket: socket.socket = None,
    ):
        super().__init__(port, address)
        self.address_family = address_family
        self.type = type
        self.socket = socket 
        