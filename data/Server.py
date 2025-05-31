from model.ServerSocket import ServerSocket
from model.Arsenal.Ships import Ship
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
        print(f"Cliente B conectado desde {address_b}")
        
        client_a.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador A"}))
        client_b.sendall(pickle.dumps({"msg": "Comienza la partida, eres el jugador B"}))
        
        clients = [client_a, client_b]
        turn = 0

        while self.is_running:
            try:
                # Recibe jugada del jugador en turno
                data = clients[turn].recv(4096)
                if not data:
                    print("Un jugador se ha desconectado.")
                    break
                jugada = pickle.loads(data)  # (row, col)
                print(f"Jugador {turn+1} ataca {jugada}")

                # Reenvía la jugada al oponente
                clients[1-turn].sendall(pickle.dumps({'attack': jugada}))

                # Cambia de turno
                turn = 1 - turn
            except Exception as e:
                print(f"Error: {e}")
                break
            
        client_a.close()
        client_b.close()
        self.server_socket.servidor.close()
        print("Servidor cerrado.")