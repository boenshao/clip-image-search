from typing import Annotated, Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel


class Image(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(unique=True)

    clip_embedding: Optional["CLIPEmbedding"] = Relationship(
        back_populates="image",
        cascade_delete=True,
        sa_relationship_kwargs={"uselist": False},
    )
    search_logs: list["SearchLog"] = Relationship(
        back_populates="image",
    )


class CLIPEmbedding(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    embedding: Any = Field(sa_column=Column(Vector(512)))
    image_id: int = Field(foreign_key="image.id", ondelete="CASCADE")

    image: Image | None = Relationship(back_populates="clip_embedding")
    search_logs: list["SearchLog"] = Relationship(
        back_populates="clip_embedding",
    )


class SearchLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    query: str
    clip_distance: float
    # this validation seems not working...https://github.com/fastapi/sqlmodel/issues/52
    # let's do it in the endpoint
    user_rating: Annotated[int, Field(ge=0, le=1)] | None

    image_id: int | None = Field(default=None, foreign_key="image.id")
    clip_embedding_id: int | None = Field(default=None, foreign_key="clipembedding.id")

    image: Image | None = Relationship(back_populates="search_logs")
    clip_embedding: CLIPEmbedding | None = Relationship(back_populates="search_logs")
