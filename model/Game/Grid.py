class Grid:
    def __init__(
        self,
        pos_X = 0,
        pos_Y = 0,
        is_occupied = False,
        is_discovered = False
    ):
        self.pos_X = pos_X
        self.pos_Y = pos_Y
        self.is_occupied = is_occupied
        self.is_discovered = is_discovered