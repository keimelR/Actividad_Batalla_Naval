from model.ServerSocket import ServerSocket
from data.Client import Client
import pickle
import socket
import threading
import queue

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_socket = ServerSocket(host, port)
        self._running_event = threading.Event()
        self.active_clients = []
        self.clients: queue.Queue = queue.Queue()

    @property
    def is_running(self):
        return self._running_event.is_set()

    def accept_player(self):
        while self.is_running:
            try:
                client_sock, address_sock = self.server_socket.servidor.accept()
                print(f"Cliente conectado desde {address_sock}")
                
                self.clients.put(item = client_sock)
            except Exception as e:
                print(f"Error al aceptar un jugador: {e}")

    def game_manager(self):
        while self.is_running:
            try:
                # Espera hasta tener dos jugadores en la cola
                client_a = self.clients.get()
                client_b = self.clients.get()
                print("Iniciando partida entre dos jugadores.")
                threading.Thread(target=self.run_game, args=(client_a, client_b), daemon=True).start()
            except queue.Empty:
                continue

    def run_game(self, client_a, client_b):
        try:
            client_a.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador A"}))
            client_b.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador B"}))

            player_boards = [None, None]

            # Recibe tableros
            try:
                data = client_a.recv(4096)
                msg = pickle.loads(data)
                player_boards[0] = msg['board']

                data = client_b.recv(4096)
                msg = pickle.loads(data)
                player_boards[1] = msg['board']
            except Exception as e:
                print(f"Error recibiendo tableros: {e}")
                client_a.close()
                client_b.close()
                return

            clients = [client_a, client_b]
            turn = 0
            active_party = True
            while active_party and self.is_running:
                try:
                    clients[turn].sendall(pickle.dumps({'msg': 'Es tu turno'}))
                    data = clients[turn].recv(4096)
                    if not data:
                        print("Un jugador se ha desconectado.")
                        clients[1 - turn].sendall(pickle.dumps({'msg': 'El oponente se ha desconectado.'}))
                        break

                    jugada = pickle.loads(data)
                    if not isinstance(jugada, dict) or 'attack' not in jugada:
                        continue

                    coords = jugada['attack']
                    if not isinstance(coords, tuple) or len(coords) != 2:
                        continue

                    row, col = coords
                    opponent = 1 - turn
                    hit = False
                    if player_boards[opponent][row][col] is not None:
                        player_boards[opponent][row][col] = None
                        hit = True

                    clients[opponent].sendall(pickle.dumps({'attack': coords, 'hit': hit}))

                    if not self.has_ships_left(player_boards[opponent]):
                        clients[turn].sendall(pickle.dumps({'result': 'win'}))
                        clients[opponent].sendall(pickle.dumps({'result': 'lose'}))
                        print(f"Jugador {turn + 1} ha ganado.")
                        break
                    else:
                        clients[turn].sendall(pickle.dumps({'result': 'continue', 'hit': hit}))
                        turn = opponent

                except Exception as e:
                    print(f"Error en el juego: {e}")
                    try:
                        clients[1 - turn].sendall(pickle.dumps({'msg': 'Error del oponente o desconexión.'}))
                    except:
                        pass
                    break

            for client in clients:
                try:
                    client.close()
                except:
                    pass

        except Exception as e:
            print(f"Error en partida: {e}")
    

    def start(self):
        try:
            self.server_socket.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.servidor.bind((self.server_socket.host, self.server_socket.port))
            self.server_socket.servidor.listen(10)
            self._running_event.set()
            print(f"Servidor escuchando en {self.server_socket.host}:{self.server_socket.port}")
        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")
            return

        
        threading.Thread(target=self.accept_player, daemon=True).start()
        threading.Thread(target=self.game_manager, daemon=True).start()

    def stop(self):
        print("Deteniendo servidor...")
        self._running_event.clear()
        try:
            self.server_socket.servidor.close()
        except:
            pass

    def has_ships_left(self, board):
        for row in board:
            for cell in row:
                if cell is not None:
                    return True
        return False
