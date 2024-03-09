import uuid

from sqlalchemy import Column, Integer, TEXT, Boolean, JSON

from models.base import BaseModel


class Game(BaseModel):
    __tablename__ = "game"
    game_id = Column(TEXT, default=uuid.uuid4().__str__())
    width = Column(Integer, nullable=False, default=0)
    height = Column(Integer, nullable=False, default=0)
    mines_count = Column(Integer, nullable=False, default=0)
    completed = Column(Boolean, nullable=False, default=0)
    field = Column(JSON, nullable=False, default={})
    map = Column(JSON, nullable=False, default={})
