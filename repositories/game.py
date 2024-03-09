import copy
import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enums.type_field import TypeField
from models import Game
from schemas.game import NewGameRequest


class GameRepository:

    def clear_map(self, field):
        copy_field = copy.deepcopy(field)
        for x in range(len(copy_field)):
            for y in range(len(copy_field[x])):
                copy_field[x][y] = TypeField.empty
        return copy_field

    def create_game(self, session: AsyncSession, data: NewGameRequest, field):
        temple = self.clear_map(field)

        new_game = Game(game_id = uuid.uuid4().__str__(),width=data.width, height=data.height, mines_count=data.mines_count, map=field, field=temple)
        session.add(new_game)
        return new_game

    async def get_game(self, session: AsyncSession, game_id:str):
        result = await session.execute(select(Game).where(Game.game_id == game_id))
        return result.scalars().one()

    async def save(self, session: AsyncSession):
        await session.commit()

