from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from depends import get_game_service
from loader import get_session_async
from schemas.Error import ErrorResponse
from schemas.game import NewGameRequest, GameInfoResponse, GameTurnRequest
from services.game import GameService

router = APIRouter(prefix="/game")


@router.post(
    "/new",
    response_model=GameInfoResponse, responses = {400: {"model": ErrorResponse}},
    description="Начало новой игры"
)
async def new(
        data: NewGameRequest,
        services: GameService = Depends(get_game_service),
        session: AsyncSession = Depends(get_session_async)
):
    return await services.new_game(session, data)


@router.post(
    "/turn",
    response_model=GameInfoResponse, responses = {400: {"model": ErrorResponse}},
    description="Ход пользователя",
)
async def turn(
        data: GameTurnRequest,
        services: GameService = Depends(get_game_service),
        session: AsyncSession = Depends(get_session_async)
):
    return await services.turn_game(session, data)
