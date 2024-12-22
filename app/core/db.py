from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session

from app.core.config import settings
from app.models import *  # noqa: F403

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    pass
