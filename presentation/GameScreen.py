import pygame
import sys
from data.Client import Client

class GameScreen:
    def __init__(self, SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_BOARD_MATRIX, client: Client):
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.player_board_matrix = PLAYER_BOARD_MATRIX

        # Cambia attacked_grids para guardar (x, y, resultado)
        self.attacked_grids: list[tuple[int, int, str]] = []
        self.enemy_attacks: list[tuple[int, int]] = []

        self.client = client

        # Conectar callbacks del cliente
        self.client.on_attack_received = self.on_attack_received
        self.client.on_result_received = self.on_result_received

        # Estado de turno y juego
        self.is_player_turn = self.client.my_turn
        self.game_over = False
        self.winner_text = ""
        self.font_game_over = None

        # Colores
        self.COLOR_SKY_BLUE = (169, 230, 255)
        self.COLOR_CLASSIC_WHITE = (241, 241, 238)
        self.COLOR_RED_IMPERIAL = (237, 41, 57)
        self.COLOR_STONE = (89, 120, 142)
        self.COLOR_BATTLESHIP = (131, 131, 128)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GREEN_HIT = (0, 200, 0)

        self.status_message = ""
        self.status_font = None
        self.turno_message = ""
        self.turno_font = None

        self.waiting_for_result = False

        self.client.on_opponent_disconnected = self.on_opponent_disconnected

        self.exit_button_rect = pygame.Rect(self.SCREEN_WIDTH - 160, 20, 120, 40)

    def start_game(self):
        pygame.init()
        pygame.font.init()
        self.status_font = pygame.font.SysFont('Arial', 28, True)
        self.font_game_over = pygame.font.SysFont('Arial', 48, True)

        screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("BattleShip")
        clock = pygame.time.Clock()
        running = True

        cell_size = 40
        columns = 10
        rows = 10

        regular_font = pygame.font.SysFont('Arial', 20, False)
        bold_font = pygame.font.SysFont('Arial', 20, True)

        text_column = ['A','B','C','D','E','F','G','H','I','J']
        text_row = ['1','2','3','4','5','6','7','8','9','10']

        player_board_origin = (50, 140)
        opponent_board_origin = (600, 140)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.exit_button_rect.collidepoint(event.pos):
                        self.exit_game()
                    elif not self.game_over and event.button == 1:
                        self.attack(*event.pos, cell_size, *opponent_board_origin, columns, rows)
                    elif self.game_over and event.button == 1:
                        running = False

            screen.fill(self.COLOR_CLASSIC_WHITE)

            self.draw_title("Tu Flota", pygame.Rect(50, 60, 400, 40), bold_font, screen, self.COLOR_RED_IMPERIAL)
            self.draw_title("Flota Enemiga", pygame.Rect(600, 60, 400, 40), bold_font, screen, self.COLOR_STONE)

            self.draw_board(screen, cell_size, *player_board_origin, text_column, text_row, columns, rows, regular_font)
            self.draw_board(screen, cell_size, *opponent_board_origin, text_column, text_row, columns, rows, regular_font)

            self.draw_player_ship(screen, cell_size, *player_board_origin, columns, rows)

            # Dibuja ataques realizados (usa color según resultado)
            for x, y, resultado in self.attacked_grids:
                color = self.COLOR_GREEN_HIT if resultado == "hit" else self.COLOR_RED_IMPERIAL
                pygame.draw.circle(screen, color, (x, y), 20)
            for x, y in self.enemy_attacks:
                pygame.draw.circle(screen, self.COLOR_STONE, (x, y), 20)

            # Mensajes de turno y estado
            self.turno_message = "Tu turno" if self.is_player_turn else "Turno enemigo"
            pygame.display.set_caption(f"BattleShip - {self.turno_message}")
            self.draw_turno_message(screen)
            if self.status_message:
                self.draw_status_message(screen)

            # Botón de salida
            self.draw_exit_button(screen)

            # Mostrar mensaje de fin de juego
            if self.game_over:
                self.show_game_over(screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def draw_exit_button(self, screen):
        pygame.draw.rect(screen, self.COLOR_RED_IMPERIAL, self.exit_button_rect, border_radius=8)
        font = pygame.font.SysFont('Arial', 22, True)
        text = font.render("Salir", True, self.COLOR_CLASSIC_WHITE)
        text_rect = text.get_rect(center=self.exit_button_rect.center)
        screen.blit(text, text_rect)

    def exit_game(self):
        try:
            # Notificar al otro cliente antes de desconectarse
            self.client.send_message({"type": "disconnect"})
            self.client.disconnect()
        except Exception as e:
            print("Error al desconectarse del servidor:", e)
        pygame.quit()
        sys.exit()

    def draw_status_message(self, screen):
        text_surface = self.status_font.render(self.status_message, True, self.COLOR_BLACK)
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, int(self.SCREEN_HEIGHT * 0.9)))
        screen.blit(text_surface, text_rect)

    def draw_turno_message(self, screen):
        text_surface = self.status_font.render(self.turno_message, True, self.COLOR_BLACK)
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 20))
        screen.blit(text_surface, text_rect)

    def draw_board(self, screen, cell_size, origin_x, origin_y, text_column, text_row, columns, rows, font):
        # Column headers
        for x in range(columns):
            rect_col = pygame.Rect(origin_x + x * cell_size, origin_y - 30, cell_size, 20)
            pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_col, 2)
            text = font.render(text_column[x], True, 'black')
            screen.blit(text, text.get_rect(center=rect_col.center))

        # Rows and cells
        for y in range(rows):
            rect_row = pygame.Rect(origin_x - 30, origin_y + y * cell_size, 20, cell_size)
            pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_row, 1)
            text = font.render(text_row[y], True, 'black')
            screen.blit(text, text.get_rect(center=rect_row.center))
            for x in range(columns):
                rect = pygame.Rect(origin_x + x * cell_size, origin_y + y * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, self.COLOR_SKY_BLUE, rect)
                pygame.draw.rect(screen, self.COLOR_STONE, rect, 1)

    def draw_title(self, title, rect, font, screen, color_bg, color_text='white'):
        pygame.draw.rect(screen, color_bg, rect, 0, 10)
        text_surface = font.render(title, True, color_text)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def draw_player_ship(self, screen, cell_size, origin_x, origin_y, columns, rows):
        for row in range(rows):
            for column in range(columns):
                if self.player_board_matrix[row][column] is not None:
                    rect = pygame.Rect(origin_x + column * cell_size, origin_y + row * cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, self.COLOR_BATTLESHIP, rect)

    def attack(self, origin_attack_x, origin_attack_y, cell_size, origin_x, origin_y, columns, rows):
        if not self.is_player_turn or self.game_over or self.waiting_for_result:
            self.status_message = "No es tu turno para atacar."
            return
        
        if (origin_x <= origin_attack_x <= origin_x + columns * cell_size and
            origin_y <= origin_attack_y <= origin_y + rows * cell_size):

            col = (origin_attack_x - origin_x) // cell_size
            row = (origin_attack_y - origin_y) // cell_size

            center_x = origin_x + col * cell_size + cell_size // 2
            center_y = origin_y + row * cell_size + cell_size // 2

            # Busca si ya atacaste esta casilla
            if not any((x == center_x and y == center_y) for x, y, _ in self.attacked_grids):
                # Guarda el ataque con resultado pendiente
                self.attacked_grids.append((center_x, center_y, "pending"))
                self.waiting_for_result = True
                self.status_message = "Esperando resultado..."
                self._last_attack_index = len(self.attacked_grids) - 1  # Guarda el índice del último ataque
                self.client.play_turn(row, col)
            else:
                self.status_message = "Ya atacaste esta casilla."
        else:
            self.status_message = "Click fuera del tablero enemigo."

    def on_attack_received(self, row, col):
        if self.game_over:
            return

        cell_size = 40
        player_board_origin = (50, 140)
        center_x = player_board_origin[0] + col * cell_size + cell_size // 2
        center_y = player_board_origin[1] + row * cell_size + cell_size // 2

        if (center_x, center_y) not in self.enemy_attacks:
            self.enemy_attacks.append((center_x, center_y))
            self.status_message = f"¡Has sido atacado en ({row + 1}, {chr(col + 65)})!"
        self.is_player_turn = True
        self.waiting_for_result = False

    def on_result_received(self, resultado):
        self.waiting_for_result = False
        if resultado == 'win':
            self.game_over = True
            self.winner_text = "¡Ganaste la partida!"
            self.status_message = self.winner_text
        elif resultado == 'lose':
            self.game_over = True
            self.winner_text = "¡Has perdido la partida!"
            self.status_message = self.winner_text
        else:
            # Actualiza el resultado del último ataque
            if hasattr(self, '_last_attack_index'):
                x, y, _ = self.attacked_grids[self._last_attack_index]
                self.attacked_grids[self._last_attack_index] = (x, y, resultado)
                del self._last_attack_index
            self.status_message = f"Resultado del ataque: {resultado}"
            self.is_player_turn = False

    def show_game_over(self, screen):
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        color = (0, 200, 0) if "Ganaste" in self.winner_text else (200, 0, 0)
        text_surface = self.font_game_over.render(self.winner_text, True, color)
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        screen.blit(text_surface, text_rect)

        subtext = self.status_font.render("Haz clic para salir", True, (255, 255, 255))
        sub_rect = subtext.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 60))
        screen.blit(subtext, sub_rect)

        pygame.display.flip()
    
    def on_opponent_disconnected(self):
        self.game_over = True
        self.winner_text = "El oponente se ha desconectado."
        self.status_message = self.winner_text
