from model.ClientSocket import ClientSocket
import socket

class Client:
    def __init__(self, client: ClientSocket = ClientSocket()):
        self.client = client
        
    def run_client(self):
        self.client.socket = socket.socket(self.client.address_family, self.client.type)
        self.client.socket.connect((self.client.address, self.client.port))
        
        while True:
            msg = input("Enter the message; ")
            self.client.socket.send(msg.encode("utf-8")[:1024])
            
            response = self.client.socket.recv(1024)
            response = response.decode("utf-8")
            
            if response.lower() == "closed":
                break
            print(f"Received: {response}")
        
        self.client.socket.close()
        print("Cerrando conexion del servidor")
        
client = Client()
client.run_client()
