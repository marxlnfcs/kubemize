class InvalidStateError(Exception):
    def __init__(self, message: str = "Corrupted or invalid state file detected."):
        self.message: str = message
        super().__init__(message)