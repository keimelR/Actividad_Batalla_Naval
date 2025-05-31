import pygame
import pygame_gui
import os
import ipaddress

from data.Server import Server
from data.Client import Client
from presentation.ServerScreen import ServerScreen
import threading

from presentation.GameScreen import GameScreen
from model.Arsenal.Ships.Ship import Ship


class PreparationScreen:
    def __init__(self, SCREEN_HEIGHT, SCREEN_WIDHT):
        # Dimensiones de la Ventana
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDHT = SCREEN_WIDHT
        # Datos del cliente y servidor
        self.port_client: str = "7777"
        self.ip_address_client: str = "127.0.0.1"
        self.port_server: str = "7777"
        
        # 2D array que almacena las posiciones de los barcos en el tablero
        self.player_board_matrix = [[None for _ in range(10)] for _ in range(10)]
        
        # Determina el barco presionado
        self.active_ship = None
        
        # Para devolver el barco
        self.original_ship_position_before_drag = None 
        
        # Almacenar posiciones originales en el 'Puerto Naval' para regresarlos alli.
        self.ship_initial_staging_positions = {} 

        # Colores
        self.COLOR_SKY_BLUE = (169, 230, 255)
        self.COLOR_CLASSIC_WHITE = (241, 241, 238)
        self.COLOR_RED_IMPERIAL = (237, 41, 57)
        self.COLOR_STONE = (89, 120, 142)
        self.COLOR_BATTLESHIP = (131, 131, 128)
        self.COLOR_GAINSBORO = (220, 220, 220)
        self.COLOR_SILVER = (192, 192, 192)

    def start_game(self):
        """ Inicia la ventana de preparacion del juego. """

        pygame.init()
        pygame.font.init()

        # Obtenemos la ubicacion del archivo theme.json (Se utiliza para decorar los elementos de la GUI)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        theme_path = os.path.join(current_dir, "theme.json")

        # ui_manager gestiona los elementos de la GUI, mientras que screen todas las funcionalidades de pygame
        ui_manager = pygame_gui.UIManager((self.SCREEN_WIDHT, self.SCREEN_HEIGHT), theme_path=theme_path)
        screen = pygame.display.set_mode((self.SCREEN_WIDHT, self.SCREEN_HEIGHT))

        pygame.display.set_caption("BattleShip")
        clock = pygame.time.Clock()
        running = True

        # Tamaño de las celdas (x, y)
        cell_size = 40
        
        columns = 10
        rows = 10

        # Fuente de palabras (Negrita y normal)
        regular_font = pygame.font.SysFont('couriernew', 20, False)
        bold_font = pygame.font.SysFont('couriernew', 20, True)

        # El texto ubicado encima de las columnas y al lado de las filas
        text_column = ['A','B','C','D','E','F','G','H','I','J']
        text_row = ['1','2','3','4','5','6','7','8','9','10']

        # Se crean los elementos relacionado al apartado de servidor (1 nput y 1 Button)
        text_port_server = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(576, 225, 378, 30),
            manager=ui_manager,
            placeholder_text="7777",
            object_id="#text_port_server"
        )

        button_server = pygame_gui.elements.UIButton(
            relative_rect= pygame.Rect(576, 270, 378, 30),
            text = "Iniciar Servidor",
            manager = ui_manager,
            object_id = "#button_server"
        )

        # Creamos los elementos relacionados al apartado de cliente (2 Input y 1 Button)
        text_port_client = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(576, 360, 378, 30),
            manager=ui_manager,
            placeholder_text="7777",
            object_id="#text_port_client"
        )
        text_ip_address_client = pygame_gui.elements.UITextEntryLine(
            relative_rect = pygame.Rect(576, 450, 378, 30),
            manager= ui_manager,
            placeholder_text="192.168.1.1",
            object_id="#text_ip_address_client"
        )

        button_client = pygame_gui.elements.UIButton(
            relative_rect= pygame.Rect(576, 495, 378, 30),
            text = "Unirse a un servidor",
            manager = ui_manager,
            object_id = "#button_client"
        )

        print("Theme cargado desde:", os.path.abspath("theme.json"))

        # Lista de barcos a utilzar
        ships: list[Ship] = []

        # Destructores (Barcos grandes)
        ships.append(Ship(50, 540, 120, 40, 3))

        # Fragatas (Barcos medianos)
        ships.append(Ship(50, 590, 80, 40, 2))
        ships.append(Ship(170, 590, 80, 40, 2))

        # Barcos de patrulla (Barcos pequeños)
        ships.append(Ship(50, 640, 40, 40, 1))
        ships.append(Ship(170, 640, 40, 40, 1))
        ships.append(Ship(290, 640, 40, 40, 1))

        # Almacenar las posiciones iniciales de los barcos
        for ship in ships:
            self.ship_initial_staging_positions[ship] = ship.rect.topleft

        # Posicion inicial del tablero del jugador (esquina superior izquierda)
        player_board_origin = (50, 110)
        
        while running:
            time_delta = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                ui_manager.process_events(event)

                # Si un boton es presionado
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    # --- BOTÓN SERVIDOR ---
                    if event.ui_element == button_server:
                        if self.port_server and self.port_server.isnumeric():
                            print(f"Iniciando servidor en el puerto: {self.port_server}")
                            # Iniciar el servidor en un hilo para no bloquear la interfaz
                            server = Server(port=int(self.port_server))
                            screen_server = ServerScreen(server)
                            screen_server.start()      
                            running = False                      
                        else:
                            print("Error: Ingrese un puerto válido para el servidor.")

                    # --- BOTÓN CLIENTE ---
                    elif event.ui_element == button_client:
                        is_ip_valid = False
                        try:
                            if self.ip_address_client:
                                ipaddress.ip_address(self.ip_address_client)
                                is_ip_valid = True
                            else:
                                print("Error: La dirección IP está vacía.")
                        except ValueError:
                            print("Error: Ingrese una dirección IP válida.")
                        except TypeError:
                            print("Error: La dirección IP no ha sido establecida.")

                        if self.port_client and self.port_client.isnumeric() and is_ip_valid:
                            print(f"Uniéndose al servidor en {self.ip_address_client}:{self.port_client}")
                            # Iniciar el cliente
                            client = Client(
                                host=self.ip_address_client,
                                port=int(self.port_client),
                                nombre="Jugador",
                                board_matrix=self.player_board_matrix
                            )
                            client.connect()
                            running = False
                            game_screen = GameScreen(
                                self.SCREEN_HEIGHT, 
                                self.SCREEN_WIDHT,
                                PLAYER_BOARD_MATRIX=self.player_board_matrix,
                                client= client
                            )
                            game_screen.start_game()
                        else:
                            if not (self.port_client and self.port_client.isnumeric()):
                                print("Error: Ingrese un puerto válido para el cliente.")

                # En caso de ser un Input para ingresar texto
                elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    # Determinamos cual Input fue presionado (los asociados a server o clientes)
                    
                    if event.ui_element == text_port_server:
                        self.port_server = event.text
                        if not self.port_server.isnumeric():
                            print(f"Puerto del servidor inválido: {event.text}. Ingrese solo números.")
                    elif event.ui_element == text_port_client:
                        self.port_client = event.text
                        if not self.port_client.isnumeric():
                            print(f"Puerto del cliente inválido: {event.text}. Ingrese solo números.")
                    elif event.ui_element == text_ip_address_client:
                        self.ip_address_client = event.text
                        try:
                            ipaddress.ip_address(self.ip_address_client)
                        except ValueError:
                            print(f"Dirección IP inválida: {event.text}")

                # --- Eventos de MOUSE para arrastrar barcos ---
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Click izquierdo
                        clicked_on_board = False
                        # Verifica si se hizo clic en el área del tablero
                        if (player_board_origin[0] <= event.pos[0] < player_board_origin[0] + columns * cell_size and
                            player_board_origin[1] <= event.pos[1] < player_board_origin[1] + rows * cell_size):
                            # Click en el tablero, intenta recoger un barco ya colocado
                            clicked_col = (event.pos[0] - player_board_origin[0]) // cell_size
                            clicked_row = (event.pos[1] - player_board_origin[1]) // cell_size
                            ship_on_cell = self.player_board_matrix[clicked_row][clicked_col]
                            if ship_on_cell:
                                self.active_ship = ship_on_cell
                                self.original_ship_position_before_drag = self.active_ship.rect.topleft
                                self.clear_ship_from_matrix(self.active_ship)
                                clicked_on_board = True
                                
                        # Si no se hizo clic en un barco del tablero, revisa los del puerto
                        if not clicked_on_board: 
                            for ship_idx, ship in enumerate(ships):
                                # Solo si no está ya en el tablero o si se clickea en él en el puerto
                                if ship.rect.collidepoint(event.pos) and not ship.is_on_grid:
                                    self.active_ship = ship
                                    self.original_ship_position_before_drag = ship.rect.topleft
                                    break
                    # Click derecho para rotar
                    if event.button == 3: 
                        if self.active_ship:
                            self.active_ship.rotate()

                # Se levanta el click, es decir, cuando dejas de presionar el boton del mouse.
                if event.type == pygame.MOUSEBUTTONUP:
                    
                    # En caso de ser el click izquierdo y que estes presionando un barco, se procedera a añadirlo en la cuadricula del tablero
                    if event.button == 1 and self.active_ship:
                        placed_successfully = self.snap_to_grid(
                            ship=self.active_ship,
                            board_origin_x=player_board_origin[0],
                            board_origin_y=player_board_origin[1],
                            cell_size=cell_size,
                            columns=columns,
                            rows=rows,
                            board_matrix=self.player_board_matrix
                        )
                        if not placed_successfully:
                            # Devuelve el barco a su posición original (ya sea en el puerto o en el tablero)
                            self.active_ship.rect.topleft = self.original_ship_position_before_drag
                            # Si el barco estaba en el grid antes de arrastrarlo y no pudo recolocarse
                            # hay que ponerlo de nuevo en la matriz en su posición original

                            print(f"No se pudo colocar {self.active_ship}. Regresando a {self.original_ship_position_before_drag}")

                        self.active_ship = None
                        self.original_ship_position_before_drag = None

                # En caso de mover el mouse
                if event.type == pygame.MOUSEMOTION:
                    if self.active_ship:
                        self.active_ship.rect.move_ip(event.rel)

                if event.type == pygame.QUIT:
                    running = False

            ui_manager.update(time_delta)
            screen.fill(self.COLOR_CLASSIC_WHITE)

            # Dibujar títulos
            self.draw_title("Tu Flota", pygame.Rect(50, 30, 400, 40), bold_font, screen, self.COLOR_RED_IMPERIAL)

            # Dibujar tableros
            self.draw_board(screen, cell_size, *player_board_origin, text_column, text_row, columns, rows, regular_font)

            # Dibujamos los titulos
            self.title_form(font=bold_font, screen= screen, ui_manager=ui_manager)

            # Dibujamos los barcos
            self.draw_ship(screen, bold_font, ships= ships)

            ui_manager.draw_ui(screen)
            pygame.display.flip()

        pygame.quit() # Esta línea debe ejecutarse después de que el bucle principal termina



    def draw_board(self, screen, cell_size, origin_x, origin_y, text_column, text_row, columns, rows, font):
        """ Dibujamos el tablero """
        
        # Imprimimos en la pantalla el texto de las columan (A, B, C, D, ..., J)
        for x in range(columns):
            rect_col = pygame.Rect(origin_x + x * cell_size, origin_y - 30, cell_size, 20)
            pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_col, 2)
            text = font.render(text_column[x], True, 'black')
            screen.blit(text, text.get_rect(center=rect_col.center))


        for y in range(rows):
            # Imprimimos en la pantalla el texto de las filas (1, 2, 3, 4, 5, ..., 10)
            rect_row = pygame.Rect(origin_x - 30, origin_y + y * cell_size, 20, cell_size)
            pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_row, 1)
            text = font.render(text_row[y], True, 'black')
            screen.blit(text, text.get_rect(center=rect_row.center))

            for x in range(columns):
                # Dibujamos el tablero con rectangulos
                rect = pygame.Rect(origin_x + x * cell_size, origin_y + y * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, self.COLOR_SKY_BLUE, rect)
                pygame.draw.rect(screen, self.COLOR_STONE, rect, 1)

    def draw_title(self, title, rect, font: pygame.font, screen, color_bg, color_text='white'):
        """ Dibujamos el titulo """
        pygame.draw.rect(screen, color_bg, rect, 0, 10)
        text_surface = font.render(title, True, color_text)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)


    def draw_ship(self, screen: pygame.Surface, font: pygame.font, ships: list[Ship]):
        """ Dibujamos los barcos del jugadr """
        
        # Dibujamos el cuadro de los barcos
        board_ship = pygame.Rect(50, 530, 400, 160)
        pygame.draw.rect(screen, self.COLOR_GAINSBORO, board_ship, 0)

        # Dibujamos los barcos
        for ship in ships:
            ship.draw(screen)

        # Texto de 'Puerto Naval'
        rect_cont_text = pygame.Rect(450, 530, 20, 160)
        pygame.draw.rect(screen, self.COLOR_CLASSIC_WHITE, rect_cont_text, 1)

        text_naval = font.render('Puerto Naval', False, 'black')
        text_rotate_naval = pygame.transform.rotate(text_naval, 270)
        text_surface = text_rotate_naval.get_rect(center = rect_cont_text.center)


        screen.blit(text_rotate_naval, text_surface)

    def clear_ship_from_matrix(self, ship: Ship):
        """ Elimina todas las referencias a este barco de la matriz del tablero. """
        for r in range(len(self.player_board_matrix)):
            for c in range(len(self.player_board_matrix[0])):
                if self.player_board_matrix[r][c] == ship:
                    self.player_board_matrix[r][c] = None
        ship.is_on_grid = False # Marcar que ya no está (o no aún) en una posición válida del grid

    def snap_to_grid(self, ship: Ship, board_origin_x: int, board_origin_y: int, cell_size: int, columns: int, rows: int, board_matrix: list[list]):
        """ Inserta los barcos en las cuadriculas del tablero """
        ship_center_x, ship_center_y = ship.rect.centerx, ship.rect.centery

        # Verifica si el centro del barco está sobre el área del tablero
        if not (board_origin_x <= ship_center_x < board_origin_x + columns * cell_size and
                board_origin_y <= ship_center_y < board_origin_y + rows * cell_size):
            ship.is_on_grid = False
            return False # No está sobre el tablero

        # Calcula la celda (col, row) más cercana al origen (top-left) del barco
        # Se añade cell_size // 2 para redondear al centro de la celda más cercana
        potential_col = (ship.rect.x - board_origin_x + cell_size // 2) // cell_size
        potential_row = (ship.rect.y - board_origin_y + cell_size // 2) // cell_size

        cells_to_occupy = []
        ship_len = ship.length
        # Determina la orientación del barco (horizontal si el ángulo es 0 o 180)
        current_orientation_horizontal = ship.angle == 0 or ship.angle == 180

        # Calcula las celdas que el barco intentaría ocupar
        for i in range(ship_len):
            if current_orientation_horizontal:
                row, col = potential_row, potential_col + i
            else:
                row, col = potential_row + i, potential_col
            cells_to_occupy.append((row, col))

        can_place = True
        for row, col in cells_to_occupy:
            # Verifica si las celdas están dentro de los límites del tablero
            if not (0 <= row < rows and 0 <= col < columns):
                can_place = False
                break
            # Verifica si las celdas ya están ocupadas por otro barco (que no sea el mismo barco)
            if board_matrix[row][col] is not None and board_matrix[row][col] != ship:
                can_place = False
                break

        if can_place:
            # Si el barco ya estaba en la matriz, lo limpia de su posición anterior
            self.clear_ship_from_matrix(ship) # Asume que esta función existe y limpia correctamente
            
            # Calcula la posición exacta en la cuadrícula
            snapped_x = board_origin_x + potential_col * cell_size
            snapped_y = board_origin_y + potential_row * cell_size
            ship.rect.topleft = (snapped_x, snapped_y) # Ajusta la posición del barco

            # Actualiza la matriz del tablero con la nueva posición del barco
            for row, col in cells_to_occupy:
                board_matrix[row][col] = ship
            ship.is_on_grid = True # Marca el barco como colocado en la cuadrícula
            return True
        else:
            ship.is_on_grid = False # Marca el barco como no colocado en la cuadrícula
            return False

    def title_form(
        self,
        font: pygame.font,
        screen: pygame.Surface,
        ui_manager: pygame_gui.UIManager
    ):
        """ Seccion de los textos acerca de cliente y servidores (NO INPUT) """
        margin_right = 576

        title = font.render("Ingrese los siguientes datos", False, 'black')
        screen.blit(title, (margin_right, 90))

        title_port_server = font.render("Puerto", False, 'black')
        screen.blit(title_port_server, (margin_right, 180))

        title_port_client = font.render("Puerto", False, 'black')
        screen.blit(title_port_client, (margin_right, 315))

        title_direction_client = font.render("Direccion IP", False, 'black')
        screen.blit(title_direction_client, (margin_right, 405))