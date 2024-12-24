import pathlib
import pickle

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models import CLIPEmbedding, Image

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


async def init_db(session: AsyncSession) -> None:
    check = await session.exec(select(CLIPEmbedding).limit(1))
    if not check.one_or_none():
        with pathlib.Path("/app/data/embeddings.pickle").open("rb") as f:  # noqa: ASYNC230
            embeddings = pickle.loads(f.read())  # noqa: S301, It's okay, I know what I'm doing

        for image_url, image_emb in embeddings:
            image = Image(url=image_url)
            emb = CLIPEmbedding(embedding=image_emb, image=image)
            session.add(image)
            session.add(emb)

        await session.commit()
