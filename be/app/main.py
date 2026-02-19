from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    allowed_origins = [
        origin.strip() for origin in settings.cors_allowed_origins.split(',') if origin.strip()
    ]
    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        lifespan=lifespan,
    )
    if settings.is_development:
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex='.*',
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    app.include_router(api_router, prefix='/api')

    @app.middleware('http')
    async def enforce_utf8_json(request: Request, call_next):
        response = await call_next(request)
        content_type = response.headers.get('content-type', '')
        if content_type.startswith('application/json') and 'charset=' not in content_type.lower():
            response.headers['content-type'] = 'application/json; charset=utf-8'
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid request.',
                'details': exc.errors(),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_, exc: HTTPException):
        if isinstance(exc.detail, dict) and {'code', 'message', 'details'}.issubset(exc.detail.keys()):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={'code': 'HTTP_ERROR', 'message': str(exc.detail), 'details': None},
        )

    @app.get('/', tags=['Root'])
    def root() -> dict[str, str]:
        return {'message': 'NetPlus backend is running'}

    return app


app = create_app()
