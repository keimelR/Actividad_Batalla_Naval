import socket
import threading
 
class ServerSocket:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente_uno = None
        self.cliente_dos = None
        self.lock = threading.Lock()
