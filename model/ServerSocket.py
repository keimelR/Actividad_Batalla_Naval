from model.ConnectionSocket import ConnectionSocket
import socket

class ServerSocket(ConnectionSocket):
    def __init__(
        self, 
        port: int = 7777, 
        address: str = "localhost",
        address_family: socket.AddressFamily = socket.AF_INET, 
        type: socket.SocketKind = socket.SOCK_STREAM,
        socket: socket.socket = None,
        number_client: int = 1
    ):
        super().__init__(port, address)
        self.address_family = address_family
        self.type = type
        self.socket = socket
        self.number_client = number_client