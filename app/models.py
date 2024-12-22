from typing import Annotated, Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel


class Image(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(unique=True)

    clip_embedding: Optional["CLIPEmbedding"] = Relationship(
        back_populates="image",
        sa_relationship_kwargs={"uselist": False},
    )
    query_logs: list["QueryLog"] = Relationship(
        back_populates="image",
    )


class CLIPEmbedding(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    embedding: Any = Field(sa_column=Column(Vector(512)))
    image_id: int | None = Field(default=None, foreign_key="image.id")

    image: Image | None = Relationship(back_populates="clip_embedding")
    query_logs: list["QueryLog"] = Relationship(
        back_populates="clip_embedding",
    )


class QueryLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    query: str
    query_score: float
    user_rating: Annotated[int, Field(ge=1, le=5)] | None
    image_id: int | None = Field(default=None, foreign_key="image.id")
    clip_embedding_id: int | None = Field(default=None, foreign_key="clipembedding.id")

    image: Image | None = Relationship(back_populates="clip_embedding")
    clip_embedding: CLIPEmbedding | None = Relationship(back_populates="clip_embedding")
