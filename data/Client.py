from model.ClientSocket import ClientSocket
import threading
import pickle
import socket

class Client:
    def __init__(self, host='localhost', port=12345, nombre="Anónimo", board_matrix=None):
        self.client_socket = ClientSocket(host, port, nombre)
        self.board_matrix = board_matrix if board_matrix else [[None]*10 for _ in range(10)]
        self.attacked_grids = set()
        self.enemy_attacks = set()
        self.my_turn = False
        self.running = True
        self.on_result_received = None
        self.on_attack_received = None
        self.on_disconnect = None  # Nuevo callback para notificar desconexión
        self.disconnect_lock = threading.Lock()
        


    def connect(self):
        try:
            self.client_socket.socket.connect((self.client_socket.host, self.client_socket.port))
            self.client_socket.conectado = True

            bienvenida = self.client_socket.socket.recv(1024)
            bienvenida_msg = pickle.loads(bienvenida)

            print("Servidor dice:", bienvenida_msg["msg"])

            serializable_board = self.get_board_serializable()
            self.client_socket.socket.sendall(pickle.dumps({'board': serializable_board}))

            if "jugador A" in bienvenida_msg["msg"]:
                self.my_turn = True

            threading.Thread(target=self.listen_for_messages, daemon=True).start()

        except (ConnectionRefusedError, socket.error, Exception) as e:
            print(f"[Error de conexión] {e}")
            self.client_socket.conectado = False
            self._handle_disconnect()

    def listen_for_messages(self):
        while self.running:
            try:
                data = self.client_socket.socket.recv(4096)
                if not data:
                    print("[Servidor] Desconectado.")
                    break

                mensaje = pickle.loads(data)

                if 'msg' in mensaje:
                    print("Mensaje del servidor:", mensaje['msg'])
                    if mensaje['msg'] == 'Es tu turno':
                        self.my_turn = True
                    elif any(keyword in mensaje['msg'].lower() for keyword in ['ganaste', 'perdiste']):
                        print("Partida terminada.")
                        break

                elif 'attack' in mensaje:
                    row, col = mensaje['attack']
                    print(f"¡Has sido atacado en ({row}, {col})!")
                    self.enemy_attacks.add((row, col))
                    if self.on_attack_received:
                        self.on_attack_received(row, col)

                elif 'result' in mensaje:
                    resultado = mensaje['result']
                    if self.on_result_received:
                        self.on_result_received(resultado)
                    if resultado in ['win', 'lose']:
                        print(f"Resultado del juego: {resultado}")
                        break

            except (EOFError, ConnectionResetError, socket.error) as e:
                print(f"[Error de conexión] {e}")
                break
            except Exception as e:
                print(f"[Error inesperado] {e}")
                break

        self.running = False
        self._handle_disconnect()

    def play_turn(self, row, col):
        if not self.my_turn:
            print("No es tu turno.")
            return

        try:
            ataque = {'attack': (row, col)}
            self.client_socket.socket.sendall(pickle.dumps(ataque))
            self.attacked_grids.add((row, col))
            self.my_turn = False
        except (socket.error, Exception) as e:
            print(f"[Error enviando ataque] {e}")
            self._handle_disconnect()

    def disconnect(self):
        self._handle_disconnect()

    def _handle_disconnect(self):
        with self.disconnect_lock:
            if not self.client_socket.conectado:
                return  # Ya desconectado

            print("[Desconectando cliente...]")
            self.running = False
            self.client_socket.conectado = False

            try:
                self.client_socket.socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass  # Puede estar ya cerrado o no conectado

            try:
                self.client_socket.socket.close()
            except Exception:
                pass

            print("[Cliente desconectado correctamente]")

            # Notificar desconexión si hay callback
            if self.on_disconnect:
                self.on_disconnect()

    def get_board_serializable(self):
        return [[1 if cell is not None else None for cell in row] for row in self.board_matrix]
