import pygame

class GameScreen:
    def __init__(self, SCREEN_HEIGHT, SCREEN_WIDHT, PLAYER_BOARD_MATRIX, is_client=False, client_or_server=None):
        # Dimensiones de la Ventana
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDHT = SCREEN_WIDHT
        
        # Tablero de la Ventana de Preparacion
        self.player_board_matrix = PLAYER_BOARD_MATRIX
        
        # Lista de Cuadriculas Atacadas
        self.attacked_grids: list[int] = []
        
        self.is_client = is_client
        self.client_or_server = client_or_server  # Puede ser un objeto Client o None

        # Conectar el callback si eres cliente
        if self.is_client and self.client_or_server:
            self.client_or_server.on_attack_received = self.on_attack_received
        
        # Colores
        self.COLOR_SKY_BLUE = (169, 230, 255)
        self.COLOR_CLASSIC_WHITE = (241, 241, 238)
        self.COLOR_RED_IMPERIAL = (237, 41, 57)
        self.COLOR_STONE = (89, 120, 142)
        self.COLOR_BATTLESHIP = (131, 131, 128)
        self.COLOR_GAINSBORO = (220, 220, 220)
        self.COLOR_SILVER = (192, 192, 192)

    """
        Metodo para iniciar el enfrentamiento entre barcos de guerra
    """
    def start_game(self):
        pygame.init()
        pygame.font.init()

        screen = pygame.display.set_mode((self.SCREEN_WIDHT, self.SCREEN_HEIGHT))
        pygame.display.set_caption("BattleShip")
        clock = pygame.time.Clock()
        running = True

        # Tamaño de la cuadricular (ancho x largo)
        cell_size = 40
        
        # Numero de filas y columnas
        columns = 10
        rows = 10

        # Fuentes de texto (Negrita y normal)
        regular_font = pygame.font.SysFont('Arial', 20, False)
        bold_font = pygame.font.SysFont('Arial', 20, True)

        # El texto ubicado encima de las columnas y al lado de las filas
        text_column = ['A','B','C','D','E','F','G','H','I','J']
        text_row = ['1','2','3','4','5','6','7','8','9','10']

        # Puntos x, y de los tableros del jugador y del oponente
        player_board_origin = (50, 140)
        opponent_board_origin = (600, 140)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Click izquierdo
                    if event.button == 1:
                        
                        # Obtenemos la posicion en donde esta ubicado el cursor
                        pos = pygame.mouse.get_pos()
                        # Realizamos un ataque (teniendo en cuenta, que solo hara el ataque dentro del tablero del oponente)
                        self.attack(*pos, cell_size, *opponent_board_origin, columns, rows)

            # Cambiamos el color de fondo
            screen.fill(self.COLOR_CLASSIC_WHITE)

            # Dibujar títulos
            self.draw_title("Tu Flota", pygame.Rect(50, 60, 400, 40), bold_font, screen, self.COLOR_RED_IMPERIAL)
            self.draw_title("Flota Enemiga", pygame.Rect(600, 60, 400, 40), bold_font, screen, self.COLOR_STONE)

            # Dibujar tableros
            self.draw_board(screen, cell_size, *player_board_origin, text_column, text_row, columns, rows, regular_font)
            self.draw_board(screen, cell_size, *opponent_board_origin, text_column, text_row, columns, rows, regular_font)

            # Los ataques realizados se muestran en pantalla
            for coord_attack_x, coord_attack_y in self.attacked_grids:
                pygame.draw.circle(screen, self.COLOR_RED_IMPERIAL, (coord_attack_x, coord_attack_y), 20)

            # Dibuja los ataques recibidos del enemigo en tu propio tablero
            if hasattr(self, 'enemy_attacks'):
                for coord_attack_x, coord_attack_y in self.enemy_attacks:
                    pygame.draw.circle(screen, self.COLOR_STONE, (coord_attack_x, coord_attack_y), 20)

            # Mostramos la posicion de los barcos del jugador (el enemigo no los ve)
            self.draw_player_ship(
                screen = screen,
                cell_size = cell_size,
                origin_x = player_board_origin[0],
                origin_y = player_board_origin[1],
                columns = columns,
                rows = rows
            )
            
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()       
        
        
    """
        Se encarga de dibujar en pantalla la posicion de los barcos del jugador
    """
    def draw_board(
        self, 
        screen: pygame.Surface, 
        cell_size: int, 
        origin_x: int, 
        origin_y: int, 
        text_column: list[str], 
        text_row: list[str], 
        columns: int, 
        rows: int, 
        font: pygame.Font
    ):
        # Muestra en pantalla los textos relacionado a las columnas (A, B, C, D, ..., J)
        for x in range(columns):
            # Los textos estan dentro de un rectangulo, para facilitar su centrado
            rect_col = pygame.Rect(origin_x + x * cell_size, origin_y - 30, cell_size, 20)
            pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_col, 2)
            text = font.render(text_column[x], True, 'black')
            screen.blit(text, text.get_rect(center=rect_col.center))

        # Muestra en pantalla los textos relacionados a las filas (1, 2, 3, 4, ..., 10) y dibujar el tablero de juego
        for y in range(rows):
            # Los textos estan dentro de un rectangulo, para facilitar su centrado
            rect_row = pygame.Rect(origin_x - 30, origin_y + y * cell_size, 20, cell_size)
            pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_row, 1)
            text = font.render(text_row[y], True, 'black')
            screen.blit(text, text.get_rect(center=rect_row.center))
            
            # Dibuja el tablero por medio de una secuencia de rectangulos
            for x in range(columns):
                rect = pygame.Rect(origin_x + x * cell_size, origin_y + y * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, self.COLOR_SKY_BLUE, rect)
                pygame.draw.rect(screen, self.COLOR_STONE, rect, 1)

    """
        Dibuja en pantalla un titulo
    """
    def draw_title(
        self, 
        title: str, 
        rect: pygame.Rect, 
        font: pygame.Font, 
        screen: pygame.Surface, 
        color_bg, 
        color_text='white'
    ):
        # El titulo esta ubicado dentro de un rectangulo para facilitar su centrado
        pygame.draw.rect(screen, color_bg, rect, 0, 10)
        text_surface = font.render(title, True, color_text)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    """
        Dibuja en pantalla los barcos del tablero del jugador
    """
    def draw_player_ship(
        self, 
        screen: pygame.Surface, 
        cell_size: int, 
        origin_x: int, 
        origin_y: int, 
        columns: int, 
        rows: int
    ):
        # Recorremos todo el tablero
        for row in range(rows):
            for column in range(columns):
                # Si detecta una posicion ocupada en el 2D array que almacena la ubicacion de los barcos, procede a dibujarlos
                if self.player_board_matrix[row][column] is not None:
                    rect = pygame.Rect(
                        origin_x + column * cell_size,
                        origin_y + row * cell_size,
                        cell_size,
                        cell_size
                    )
                    pygame.draw.rect(screen, self.COLOR_BATTLESHIP, rect)

    """
        Se encarga de realizar el ataque a el tablero enemigo
    """
    def attack(
        self, 
        origin_attack_x: int, 
        origin_attack_y: int, 
        cell_size: int, 
        origin_x: int, 
        origin_y: int, 
        columns: int, 
        rows: int
    ):
        # Si la cuadricular presionada esta dentro del tablero del enemigo
        if  (origin_x <= origin_attack_x <= origin_x + rows * cell_size and 
            origin_y <= origin_attack_y <= origin_y + columns * cell_size):
            
            # Obtenemos la fila y columna
            col = (origin_attack_x - origin_x) // cell_size
            row = (origin_attack_y - origin_y) // cell_size
            
            # Conseguimos el centro de la cuadricula
            center_row = origin_x + col * cell_size + cell_size // 2
            center_col = origin_y + row * cell_size + cell_size // 2
                                    
            attack_point = (center_row, center_col)
            
            # Determinamos si la cuadricula a ocupar ya se encontraba en uso antiguamente, es decir, si ya habia sido ocupada.
            if attack_point not in [tuple(point) for point in self.attacked_grids]:
                self.attacked_grids.append([center_row, center_col])

                # --- INTEGRACIÓN CON RED ---
                if self.is_client and self.client_or_server:
                    resultado = self.client_or_server.play_turn(row, col)
                    if resultado == 'win':
                        print("¡Ganaste la partida!")
                        pygame.quit()
                        exit()
                    elif resultado == 'lose':
                        print("¡El servidor ha ganado!")
                        pygame.quit()
                        exit()
                # Si eres el servidor, aquí podrías implementar la lógica para mostrar el ataque del cliente
            else:
                print("Ya presionaste esta cuadricula")
        else:
            print("No cumple")
            
    def on_attack_received(self, row, col):
        # Marca la celda atacada en tu tablero (puedes usar un valor especial, por ejemplo "X")
        # Aquí simplemente dibujaremos un círculo rojo en la celda atacada
        cell_size = 40  # Usa el mismo valor que en start_game
        player_board_origin = (50, 140)
        center_x = player_board_origin[0] + col * cell_size + cell_size // 2
        center_y = player_board_origin[1] + row * cell_size + cell_size // 2
        # Guarda el ataque para dibujarlo en el render loop
        if not hasattr(self, 'enemy_attacks'):
            self.enemy_attacks = []
        self.enemy_attacks.append((center_x, center_y))
        print(f"¡Has sido atacado en ({row}, {col})!")