class ConnectionSocket:
    def __init__(
        self,
        port: int = 7777,
        address: str = "localhost"
    ):
        self.port = port
        self.address = address