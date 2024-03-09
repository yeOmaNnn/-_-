import copy
import random

from sqlalchemy.exc import NoResultFound

from enums.type_field import TypeField
from models import Game
from repositories.game import GameRepository
from schemas.Error import ErrorException
from schemas.game import NewGameRequest, GameInfoResponse, GameTurnRequest


class GameService:

    def __init__(self, repository: GameRepository):
        self.repository = repository

    def _generate_map(self, width: int, height: int, bombs: int):
        board = [[0 for _ in range(width)] for _ in range(height)]

        mines = random.sample(range(width * height), bombs)
        for mine in mines:
            row = mine // height
            col = mine % height
            board[row][col] = -1


        for x in range(width):
            for y in range(height):
                if board[x][y] != -1:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if 0 <= x + i < width and 0 <= y + j < height and board[x + i][y + j] == -1:
                                board[x][y] += 1
        return board

    def _generate_board(self, width: int, height: int, bombs: int):
        board = self._generate_map(width, height, bombs)
        type_mapping = {0: TypeField.empty, -1: TypeField.mine}
        for x in range(width):
            for y in range(height):
                board[x][y] = TypeField(str(board[x][y])) if board[x][y] not in type_mapping else type_mapping[
                    board[x][y]]
        return board

    def _check_end(self, field):
        return sum(1 for row in field for item in row if item != TypeField.mine and item != TypeField.empty)

    def _turn(self, row: int, col: int, game_map, field, width, height, mines_count):
        def reveal(row: int, col: int):
            stack = [(row, col)]
            visited = set()

            while stack:
                row, col = stack.pop()
                if (row, col) in visited:
                    continue

                if not (0 <= row < width and 0 <= col < height) or game_map[row][col] == TypeField.mine or field[row][
                    col] == TypeField.visit:
                    continue

                if game_map[row][col] == TypeField.empty:
                    field[row][col] = TypeField.zero
                    neighbors = [(row + a, col + b) for a in range(-1, 2) for b in range(-1, 2)]
                    for c, r in neighbors:
                        if (c, r) not in visited and 0 <= c < width and 0 <= r < height:
                            stack.append((c, r))
                else:
                    field[row][col] = game_map[row][col]

                visited.add((row, col))

        if game_map[row][col] == TypeField.mine:
            for x in range(height):
                for y in range(width):
                    if game_map[x][y] == TypeField.empty:
                        game_map[x][y] = TypeField.zero
            return game_map, field, True

        reveal(row, col)
        if self._check_end(field) == width * height - mines_count:
            for x in range(height):
                for y in range(width):
                    if game_map[x][y] == TypeField.mine:
                        game_map[x][y] = TypeField.visit
                    elif game_map[x][y] == TypeField.empty:
                        game_map[x][y] = TypeField.zero
            return game_map, field, True

        return game_map, field, False

    async def new_game(self, session, data: NewGameRequest):
        board = self._generate_board(data.width, data.height, data.mines_count)
        game = self.repository.create_game(session, data, board)
        await self.repository.save(session)

        field = game.map if game.completed else game.field
        return GameInfoResponse(game_id=game.game_id, width=data.width, height=data.height,
                                mines_count=data.mines_count, completed=game.completed, field=field)

    async def turn_game(self, session, data: GameTurnRequest):
        try:
            game:Game = await self.repository.get_game(session, data.game_id)

            if game.completed:
                raise ErrorException("игра завершена")

            if not 0 <= data.row < len(game.map):
                raise ErrorException(f"ряд должен быть неотрицательным и менее высоты {len(game.map)}")
            if not 0 <= data.col < len(game.map[0]):
                raise ErrorException(f"колонка должна быть неотрицательной и менее ширины {len(game.map[0])}")
            if game.field[data.row][data.col] != TypeField.empty:
                raise ErrorException(f"уже открытая ячейка")
            game.map, game.field, game.completed = self._turn(data.row, data.col, copy.deepcopy(game.map),
                                                              copy.deepcopy(game.field), game.width, game.height,
                                                              game.mines_count)
            await self.repository.save(session)

            return GameInfoResponse(game_id=game.game_id, width=game.width, height=game.height,
                                    mines_count=game.mines_count, completed=game.completed,
                                    field=game.field if not game.completed else game.map)
        except NoResultFound:
            raise ErrorException(f"игра с идентификатором {data.game_id} не была создана или устарела (неактуальна)")
