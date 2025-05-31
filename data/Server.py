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

                resultado = 'continue'  # Opciones: 'continue', 'win', 'lose'

                # Reenviar la jugada al oponente para que actualice su estado
                clients[1 - turn].sendall(pickle.dumps({'attack': coords}))

                # Enviar resultado al jugador que atacó
                clients[turn].sendall(pickle.dumps({'result': resultado}))

                if resultado == 'win':
                    # Si gana, informar y cerrar juego
                    clients[turn].sendall(pickle.dumps({'msg': '¡Ganaste la partida!'}))
                    clients[1 - turn].sendall(pickle.dumps({'msg': '¡Has perdido la partida!'}))
                    print(f"Jugador {turn + 1} ha ganado.")
                    break
                elif resultado == 'lose':
                    # Caso contrario, jugador pierde (opcional según lógica)
                    print(f"Jugador {turn + 1} ha perdido (caso no común).")
                    break
                else:
                    # Cambiar turno sólo si resultado es 'continue'
                    turn = 1 - turn

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
