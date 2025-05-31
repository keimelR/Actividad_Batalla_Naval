from model.ServerSocket import ServerSocket
import pickle

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_socket = ServerSocket(host, port)
        self.is_running = False

    def start(self):
        self.server_socket.servidor.bind((self.server_socket.host, self.server_socket.port))
        self.server_socket.servidor.listen(2)
        self.is_running = True
        print(f"Servidor escuchando en {self.server_socket.host}:{self.server_socket.port}")

        client_a, address_a = self.server_socket.servidor.accept()
        print(f"Jugador A conectado desde {address_a}")

        client_b, address_b = self.server_socket.servidor.accept()
        print(f"Jugador B conectado desde {address_b}")

        client_a.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador A"}))
        client_b.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador B"}))
        
        # Recibe el tablero de cada cliente al inicio
        player_boards = [None, None]
        data = client_a.recv(4096)
        msg = pickle.loads(data)
        player_boards[0] = msg['board']

        data = client_b.recv(4096)
        msg = pickle.loads(data)
        player_boards[1] = msg['board']
        
        clients = [client_a, client_b]
        turn = 0  # 0 para A, 1 para B

        while self.is_running:
            try:
                # Avisar al jugador que es su turno
                clients[turn].sendall(pickle.dumps({'msg': 'Es tu turno'}))
                print(f"Esperando jugada del Jugador {turn + 1}")

                # Recibe jugada del jugador en turno
                data = clients[turn].recv(4096)
                if not data:
                    print("Un jugador se ha desconectado.")
                    clients[1 - turn].sendall(pickle.dumps({'msg': 'El oponente se ha desconectado.'}))
                    break

                jugada = pickle.loads(data)

                # Validar formato de jugada
                if not isinstance(jugada, dict) or 'attack' not in jugada:
                    print(f"Mensaje inválido recibido: {jugada}")
                    # Repetir turno actual porque hubo error
                    continue

                coords = jugada['attack']
                if not isinstance(coords, tuple) or len(coords) != 2:
                    print(f"Jugada inválida recibida: {coords}")
                    # Repetir turno actual
                    continue

                print(f"Jugador {turn + 1} ataca {coords}")

                # Aquí puedes implementar la lógica para validar ataque:
                # Por ejemplo, verificar si coords es un ataque válido, si toca barco,
                # si el jugador gana, etc.
                # Por ahora simularemos resultado 'continue' para seguir el juego.
                
                # Marcar el impacto en el tablero del oponente
                row, col = coords
                opponent = 1 - turn
                hit = False
                if player_boards[opponent][row][col] is not None:
                    player_boards[opponent][row][col] = None  # Marcar como impactado
                    hit = True

                # Reenviar la jugada al oponente para que actualice su estado
                clients[opponent].sendall(pickle.dumps({'attack': coords, 'hit': hit}))
                      
                # Verificar si quedan barcos
                if not self.has_ships_left(player_boards[opponent]):
                    clients[turn].sendall(pickle.dumps({'result': 'win'}))
                    clients[opponent].sendall(pickle.dumps({'result': 'lose'}))
                    print(f"Jugador {turn + 1} ha ganado.")
                    break
                else:
                    # Enviar resultado al atacante
                    clients[turn].sendall(pickle.dumps({'result': 'continue', 'hit': hit}))
                    # Cambiar turno
                    turn = opponent

            except Exception as e:
                print(f"Error: {e}")
                try:
                    clients[1 - turn].sendall(pickle.dumps({'msg': 'Error del oponente o desconexión.'}))
                except:
                    pass
                break

        client_a.close()
        client_b.close()
        self.server_socket.servidor.close()
        print("Servidor cerrado.")

    def has_ships_left(self, board):
        for row in board:
            for cell in row:
                if cell is not None:
                    return True
        return False
