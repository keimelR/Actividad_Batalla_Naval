from model.ServerSocket import ServerSocket
import pickle
import socket
import threading

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_socket = ServerSocket(host, port)
        self._running_event = threading.Event()
        self.active_clients = []

    @property
    def is_running(self):
        return self._running_event.is_set()

    def start(self):
        try:
            self.server_socket.servidor.bind((self.server_socket.host, self.server_socket.port))
            self.server_socket.servidor.listen(2)
            self._running_event.set()
            print(f"Servidor escuchando en {self.server_socket.host}:{self.server_socket.port}")
        except Exception as e:
            print(f"Error al iniciar el servidor: {e}")
            return

        while self.is_running:
            try:
                client_a, address_a = self.server_socket.servidor.accept()
                print(f"Jugador A conectado desde {address_a}")
                self.active_clients.append(client_a)

                client_b, address_b = self.server_socket.servidor.accept()
                print(f"Jugador B conectado desde {address_b}")
                self.active_clients.append(client_b)

                if not self.is_running:
                    client_a.close()
                    client_b.close()
                    break

                client_a.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador A"}))
                client_b.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador B"}))

                player_boards = [None, None]

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
                    continue

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
                            clients[turn].sendall(pickle.dumps({'result': 'win', 'hit': hit}))
                            clients[opponent].sendall(pickle.dumps({'result': 'lose', 'hit': hit}))
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
                    if client in self.active_clients:
                        self.active_clients.remove(client)

            except socket.error as e:
                if self.is_running:
                    print(f"Error aceptando conexión: {e}")
                else:
                    break

        self.server_socket.servidor.close()
        self._running_event.clear()
        print("Servidor cerrado.")

    def stop(self):
        print("Deteniendo servidor...")
        self._running_event.clear()

        # Cerrar todos los clientes activos
        for client in self.active_clients:
            try:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            except:
                pass
        self.active_clients.clear()

        # Conectarse a sí mismo para desbloquear el accept()
        try:
            dummy_socket = socket.socket()
            dummy_socket.connect((self.server_socket.host, self.server_socket.port))
            dummy_socket.close()
        except:
            pass

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
