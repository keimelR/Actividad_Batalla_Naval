from model.ClientSocket import ClientSocket
import threading
import pickle

class Client:
    def __init__(self, host='localhost', port=12345, nombre="Anónimo", board_matrix=None):
        self.client_socket = ClientSocket(host, port, nombre)
        self.board_matrix = board_matrix if board_matrix else [[None]*10 for _ in range(10)]
        self.attacked_grids = set()
        self.enemy_attacks = set()
        self.my_turn = False
        self.running = True

    def connect(self):
        try:
            self.client_socket.socket.connect((self.client_socket.host, self.client_socket.port))
            self.client_socket.conectado = True
            bienvenida = self.client_socket.socket.recv(1024)
            bienvenida_msg = pickle.loads(bienvenida)
            print("Servidor dice:", bienvenida_msg["msg"])
            # Inicia hilo para escuchar ataques del rival
            threading.Thread(target=self.listen_for_attacks, daemon=True).start()
        except Exception as e:
            print(f"Error al conectar: {e}")
            self.client_socket.conectado = False

    def listen_for_attacks(self):
        while self.running:
            try:
                data = self.client_socket.socket.recv(4096)
                if not data:
                    print("Servidor desconectado.")
                    self.running = False
                    break
                mensaje = pickle.loads(data)
                if 'attack' in mensaje:
                    row, col = mensaje['attack']
                    print(f"¡Has sido atacado en ({row}, {col})!")
                    self.enemy_attacks.add((row, col))
                    self.my_turn = True  # Ahora es tu turno
            except Exception as e:
                print(f"Error en recepción: {e}")
                self.running = False
                break

    def play_turn(self, row, col):
        if not self.my_turn:
            print("No es tu turno.")
            return
        # Enviar jugada al servidor
        self.client_socket.socket.sendall(pickle.dumps((row, col)))
        self.attacked_grids.add((row, col))
        self.my_turn = False  # Espera el ataque del rival

    def disconnect(self):
        self.running = False
        self.client_socket.socket.close()
        self.client_socket.conectado = False