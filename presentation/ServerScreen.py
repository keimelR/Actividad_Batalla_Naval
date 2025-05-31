import pygame
import threading
from data.Server import Server

class ServerScreen:
    def __init__(
        self,
        server: Server
    ):
        self.server = server
        
    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 200))
        pygame.display.set_caption("Estado del Servidor")
        font = pygame.font.SysFont(None, 36)
        clock = pygame.time.Clock()

        # Iniciar el servidor en un hilo aparte
        server_thread = threading.Thread(target=self.server.start, daemon=True)
        server_thread.start()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((30, 30, 30))
            if self.server.is_running:
                text = font.render("El server está corriendo", True, (0, 255, 0))
            else:
                text = font.render("Server cerrado", True, (255, 0, 0))
            rect = text.get_rect(center=(200, 100))
            screen.blit(text, rect)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()