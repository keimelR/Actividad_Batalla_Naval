import pygame
import sys
from data.Client import Client

class GameScreen:
    def __init__(self, SCREEN_HEIGHT, SCREEN_WIDHT, PLAYER_BOARD_MATRIX, client: Client):
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDHT = SCREEN_WIDHT
        self.player_board_matrix = PLAYER_BOARD_MATRIX
        
        self.attacked_grids: list[int] = []
        self.enemy_attacks = []

        self.client = client
        self.client.on_attack_received = self.on_attack_received

        # Controlar estado de partida
        self.is_player_turn = self.client.my_turn
        self.game_over = False
        self.winner_text = ""
        self.font_game_over = None

        # Colors
        self.COLOR_SKY_BLUE = (169, 230, 255)
        self.COLOR_CLASSIC_WHITE = (241, 241, 238)
        self.COLOR_RED_IMPERIAL = (237, 41, 57)
        self.COLOR_STONE = (89, 120, 142)
        self.COLOR_BATTLESHIP = (131, 131, 128)
        

    def start_game(self):
        pygame.init()
        pygame.font.init()
        self.font_game_over = pygame.font.SysFont('Arial', 48, True)

        screen = pygame.display.set_mode((self.SCREEN_WIDHT, self.SCREEN_HEIGHT))
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
                
                if self.client.running is False:
                    running = False
                    break
                
                if event.type == pygame.QUIT:
                    running = False
                if not self.game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        pos = pygame.mouse.get_pos()
                        self.attack(*pos, cell_size, *opponent_board_origin, columns, rows)

            screen.fill(self.COLOR_CLASSIC_WHITE)

            self.draw_title("Tu Flota", pygame.Rect(50, 60, 400, 40), bold_font, screen, self.COLOR_RED_IMPERIAL)
            self.draw_title("Flota Enemiga", pygame.Rect(600, 60, 400, 40), bold_font, screen, self.COLOR_STONE)

            self.draw_board(screen, cell_size, *player_board_origin, text_column, text_row, columns, rows, regular_font)
            self.draw_board(screen, cell_size, *opponent_board_origin, text_column, text_row, columns, rows, regular_font)

            for coord_attack_x, coord_attack_y in self.attacked_grids:
                pygame.draw.circle(screen, self.COLOR_RED_IMPERIAL, (coord_attack_x, coord_attack_y), 20)

            for coord_attack_x, coord_attack_y in self.enemy_attacks:
                pygame.draw.circle(screen, self.COLOR_STONE, (coord_attack_x, coord_attack_y), 20)

            self.draw_player_ship(
                screen = screen,
                cell_size = cell_size,
                origin_x = player_board_origin[0],
                origin_y = player_board_origin[1],
                columns = columns,
                rows = rows
            )
            
            turno_text = "Tu turno" if self.is_player_turn else "Turno enemigo"
            pygame.display.set_caption(f"BattleShip - {turno_text}")

            # Si la partida terminó, mostrar mensaje y esperar unos segundos para cerrar
            if self.game_over:
                self.show_game_over(screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def show_game_over(self, screen):
        overlay = pygame.Surface((self.SCREEN_WIDHT, self.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        text_surface = self.font_game_over.render(self.winner_text, True, (255,255,255))
        text_rect = text_surface.get_rect(center=(self.SCREEN_WIDHT//2, self.SCREEN_HEIGHT//2))
        screen.blit(text_surface, text_rect)

        # Esperar 3 segundos y luego salir
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

    def draw_board(self, screen, cell_size, origin_x, origin_y, text_column, text_row, columns, rows, font):
        for x in range(columns):
            rect_col = pygame.Rect(origin_x + x * cell_size, origin_y - 30, cell_size, 20)
            pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_col, 2)
            text = font.render(text_column[x], True, 'black')
            screen.blit(text, text.get_rect(center=rect_col.center))

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
                    rect = pygame.Rect(
                        origin_x + column * cell_size,
                        origin_y + row * cell_size,
                        cell_size,
                        cell_size
                    )
                    pygame.draw.rect(screen, self.COLOR_BATTLESHIP, rect)

    def attack(self, origin_attack_x, origin_attack_y, cell_size, origin_x, origin_y, columns, rows):
        if not self.is_player_turn or self.game_over:
            print("No es tu turno para atacar o el juego terminó.")
            return
        
        if (origin_x <= origin_attack_x <= origin_x + columns * cell_size and
            origin_y <= origin_attack_y <= origin_y + rows * cell_size):

            col = (origin_attack_x - origin_x) // cell_size
            row = (origin_attack_y - origin_y) // cell_size

            center_x = origin_x + col * cell_size + cell_size // 2
            center_y = origin_y + row * cell_size + cell_size // 2

            attack_point = (center_x, center_y)

            if attack_point not in [tuple(point) for point in self.attacked_grids]:
                self.attacked_grids.append([center_x, center_y])

                resultado = self.client.play_turn(row, col)
                if resultado == 'win':
                    self.game_over = True
                    self.winner_text = "¡Ganaste la partida!"
                    print(self.winner_text)
                elif resultado == 'lose':
                    self.game_over = True
                    self.winner_text = "¡Has perdido la partida!"
                    print(self.winner_text)
                else:
                    self.is_player_turn = False
                    print("Turno del enemigo.")
            else:
                print("Ya presionaste esta cuadricula")
        else:
            print("Click fuera del tablero enemigo")

    def on_attack_received(self, row, col):
        if self.game_over:
            return

        cell_size = 40
        player_board_origin = (50, 140)
        center_x = player_board_origin[0] + col * cell_size + cell_size // 2
        center_y = player_board_origin[1] + row * cell_size + cell_size // 2

        self.enemy_attacks.append((center_x, center_y))
        print(f"¡Has sido atacado en ({row}, {col})!")

        self.is_player_turn = True
        print("Es tu turno.")
