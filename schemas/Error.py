from pydantic import BaseModel


class ErrorException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ErrorResponse(BaseModel):
    error: str = None
