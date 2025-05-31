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
        self.on_attack_received = None  # Callback para notificar ataque recibido

    def connect(self):
        try:
            self.client_socket.socket.connect((self.client_socket.host, self.client_socket.port))
            self.client_socket.conectado = True

            bienvenida = self.client_socket.socket.recv(1024)
            bienvenida_msg = pickle.loads(bienvenida)

            print("Servidor dice:", bienvenida_msg["msg"])

            # Detectar si este cliente es el jugador A
            if "jugador A" in bienvenida_msg["msg"]:
                self.my_turn = True  # Jugador A inicia

            # Inicia hilo para escuchar mensajes del servidor
            threading.Thread(target=self.listen_for_messages, daemon=True).start()

        except Exception as e:
            print(f"Error al conectar: {e}")
            self.client_socket.conectado = False

    def listen_for_messages(self):
        while self.running:
            try:
                data = self.client_socket.socket.recv(4096)
                if not data:
                    print("Servidor desconectado.")
                    self.running = False
                    break

                mensaje = pickle.loads(data)

                if 'msg' in mensaje:
                    print("Mensaje del servidor:", mensaje['msg'])

                    # Activar turno si el servidor lo indica
                    if mensaje['msg'] == 'Es tu turno':
                        self.my_turn = True

                    # Mensajes de fin de partida o desconexión
                    if 'ganaste' in mensaje['msg'].lower() or 'perdiste' in mensaje['msg'].lower():
                        print("Partida terminada.")
                        self.running = False
                        break

                elif 'attack' in mensaje:
                    row, col = mensaje['attack']
                    print(f"¡Has sido atacado en ({row}, {col})!")
                    self.enemy_attacks.add((row, col))
                    if self.on_attack_received:
                        self.on_attack_received(row, col)

                elif 'result' in mensaje:
                    resultado = mensaje['result']
                    print(f"Resultado de tu ataque: {resultado}")
                    # Aquí podrías reaccionar al resultado, por ejemplo actualizar UI, tablero, etc.

            except Exception as e:
                print(f"Error en recepción: {e}")
                self.running = False
                break

    def play_turn(self, row, col):
        if not self.my_turn:
            print("No es tu turno.")
            return

        try:
            ataque = {'attack': (row, col)}  # Enviar diccionario con clave 'attack'
            self.client_socket.socket.sendall(pickle.dumps(ataque))
            self.attacked_grids.add((row, col))
            self.my_turn = False
        except Exception as e:
            print(f"Error enviando ataque: {e}")

    def disconnect(self):
        self.running = False
        try:
            self.client_socket.socket.close()
        except Exception:
            pass
        self.client_socket.conectado = False
