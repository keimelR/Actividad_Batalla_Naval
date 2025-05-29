from model.Game.Grid import Grid
class Board:
    def __init__(
        self,
        len_row = 10,
        len_column = 10,
        board: list[list[Grid]] = [[]]
    ):
        self.len_row = len_row
        self.len_column = len_column
        self.board = board