import pygame
import threading
from data.Server import Server

class ServerScreen:
    def __init__(self, server: Server):
        self.server = server

    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 250))  # Aumenta el alto para el botón
        pygame.display.set_caption("Estado del Servidor")
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        button_font = pygame.font.SysFont(None, 28)
        clock = pygame.time.Clock()

        # Iniciar el servidor en un hilo aparte
        server_thread = threading.Thread(target=self.server.start, daemon=True)
        server_thread.start()

        # Definimos la posición y tamaño del botón
        button_rect = pygame.Rect(125, 180, 150, 40)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.server.stop()  # Detiene el servidor de forma segura

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button_rect.collidepoint(event.pos):
                        print("Botón presionado: Detener servidor")
                        self.server.stop()
                        running = False

            screen.fill((30, 30, 30))

            # Mostrar estado del servidor
            if self.server.is_running and server_thread.is_alive():
                status_text = font.render("El server está corriendo", True, (0, 255, 0))
            else:
                status_text = font.render("Server cerrado", True, (255, 0, 0))

            status_rect = status_text.get_rect(center=(200, 60))
            screen.blit(status_text, status_rect)

            # Mostrar IP y puerto desde ServerSocket
            ip = self.server.server_socket.host
            port = self.server.server_socket.port

            ip_text = small_font.render(f"IP: {ip}", True, (255, 255, 255))
            port_text = small_font.render(f"Puerto: {port}", True, (255, 255, 255))
            screen.blit(ip_text, (20, 120))
            screen.blit(port_text, (20, 150))

            # Dibujar el botón
            pygame.draw.rect(screen, (200, 0, 0), button_rect)
            button_text = button_font.render("Cerrar Servidor", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)

            pygame.display.flip()
            clock.tick(30)

        self.server.stop()
