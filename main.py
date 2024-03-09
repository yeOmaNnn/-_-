from urllib.request import Request

from fastapi import FastAPI, HTTPException, Query
import uvicorn
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from routers.game import router as game_router
from schemas.Error import ErrorException

app = FastAPI(title="Игра Сапёр (Minesweeper)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"], )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Overrides FastAPI default status code for validation errors from 422 to 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"error": "Отсутствует/или не правильный из параметров"}),
    )
@app.exception_handler(ErrorException)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"error": str(exc)}),
    )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes
    )

    http_methods = ["post", "get", "put", "delete"]
    # look for the error 422 and removes it
    for method in openapi_schema["paths"]:
        for m in http_methods:
            try:
                del openapi_schema["paths"][method][m]["responses"]["422"]
            except KeyError:
                pass

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(game_router,tags=["Minesweeper"])
if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)
