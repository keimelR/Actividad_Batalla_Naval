import socket
import threading
import queue

class ClientSocket:
    def __init__(self, host='localhost', port=12345, nombre="Anónimo"):
        self.host = host
        self.port = port
        self.nombre = nombre
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conectado = False
        self.cola_entrada = queue.Queue()
        self.cola_salida = queue.Queue()