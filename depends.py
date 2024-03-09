from repositories.game import GameRepository
from services.game import GameService

game_repository = GameRepository()
game_service = GameService(game_repository)


def get_game_service() -> GameService:
    return game_service
