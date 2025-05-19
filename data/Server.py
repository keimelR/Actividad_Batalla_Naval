from model.ServerSocket import ServerSocket
import socket

class Server:
    def __init__(self, server: ServerSocket = ServerSocket()):
        self.server = server

    def create_server(self):
        self.server.socket = socket.socket(family = self.server.address_family, type = self.server.type)
        self.server.socket.bind((self.server.address, self.server.port))
        self.server.socket.listen(self.server.number_client)
        
        client_socket, client_address = self.server.socket.accept()
        
        while True:
            request: bytes = client_socket.recv(1024)
            request.decode("utf-8")
            
            if request.lower == "close":
                client_socket.send("closed".encode("utf-8"))
                break
            
            print(f"Received: {request}")
            
            response: bytes = "acepted".encode("utf-8")
            client_socket.send(response)
            
        print("Conexion con el cliente cerrada")
        client_socket.close()
        
        self.server.socket.close()