from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .deps import CLIPText, get_clip_text_model, get_db
from .models import CLIPEmbedding, SearchLog

router = APIRouter()


class SearchResult(BaseModel):
    image_url: str
    search_log_id: int | None


@router.get("/search")
async def search(
    query: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    clip_text_model: Annotated[CLIPText, Depends(get_clip_text_model)],
) -> SearchResult:
    text_embeds = clip_text_model(query)
    res = (
        await db.exec(
            select(
                CLIPEmbedding,
                CLIPEmbedding.embedding.cosine_distance(text_embeds[0].tolist()).label(
                    "dist"
                ),
            )
            .order_by("dist")
            .options(selectinload(CLIPEmbedding.image))  # type: ignore
            .limit(1)
        )
    ).one_or_none()

    if not res:
        raise HTTPException(status_code=404, detail="No image found")
        # no embedding found, but this should not happen in the real world

    emb, dist = res
    search_log = SearchLog(
        query=query,
        clip_distance=dist,
        user_rating=None,
        image_id=emb.image.id,
        clip_embedding_id=emb.id,
    )

    db.add(search_log)
    await db.commit()
    await db.refresh(search_log)

    return SearchResult(image_url=emb.image.url, search_log_id=search_log.id)


class Rating(BaseModel):
    score: int = Field(ge=0, le=1)


@router.patch("/rating/{search_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def rating(
    search_log_id: int,
    rating: Rating,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    res = await db.exec(select(SearchLog).where(SearchLog.id == search_log_id))

    search_log = res.one_or_none()
    if not search_log:
        raise HTTPException(status_code=404, detail="Search log not found")

    search_log.user_rating = rating.score
    db.add(search_log)
    await db.commit()
