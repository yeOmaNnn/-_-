import uuid

from pydantic import BaseModel, Field, validator

from enums.type_field import TypeField
from schemas.Error import ErrorException


class NewGameRequest(BaseModel):
    width: int = Field(description="Ширина игрового поля", example=10)
    height: int = Field(description="Высота игрового поля", example=10)
    mines_count: int = Field(description="Количество мин на поле", example=10)

    @validator('width')
    def check_width(cls, v, values):
        if v < 2 or v > 30:
            raise ErrorException(f'ширина поля должна быть не менее 2 и не более 30')
        return v

    @validator('height')
    def check_height(cls, v, values):
        if v < 2 or v > 30:
            raise ErrorException(f'высота поля должна быть не менее 2 и не более 30')
        return v

    @validator('mines_count')
    def check_mines_count(cls, v, values):
        if v > values['width'] * values['height'] - 1:
            raise ErrorException(
                f'количество мин должно быть не менее 1 и не более {values['width'] * values['height'] - 1}')
        return v


class GameTurnRequest(BaseModel):
    game_id: str = Field(description="Ширина игрового поля", example="db4f96bb-18c9-4c1b-8ed0-a9c7baaf53ce")
    col: int = Field(description="Колонка проверяемой ячейки (нумерация с нуля)", example=10)
    row: int = Field(description="Ряд проверяемой ячейки (нумерация с нуля)", example=10)


class GameInfoResponse(BaseModel):
    game_id: str = Field(description="Ширина игрового поля", example="db4f96bb-18c9-4c1b-8ed0-a9c7baaf53ce")
    width: int = Field(description="Ширина игрового поля", example=10)
    height: int = Field(description="Высота игрового поля", example=10)
    mines_count: int = Field(description="Количество мин на поле", example=10)
    completed: bool = Field(description="Завершена ли игра", example=False)
    field: list[list[TypeField]] = Field(description="Строки минного поля (количество равно высоте height)")

    class Config:
        orm_mode = True
        from_attributes = True
