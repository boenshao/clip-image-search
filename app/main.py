import logging
from typing import Annotated

import torch
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import Field
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from transformers import AutoTokenizer, CLIPTextModelWithProjection

from .deps import get_db
from .models import CLIPEmbedding, SearchLog

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

model = CLIPTextModelWithProjection.from_pretrained("openai/clip-vit-base-patch32")
tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")


app = FastAPI()


@app.get("/")
async def read_root() -> dict:
    return {"Hello": "World"}


@app.get("/search")
async def search(
    query: str, db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:  # TODO: return schema
    inputs = tokenizer([query], padding=True, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    text_embeds = outputs.text_embeds / outputs.text_embeds.norm(
        p=2, dim=-1, keepdim=True
    )
    text_embeds = text_embeds.detach().numpy()

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
    ).one()  # FIXME

    emb, dist = res  # maybe None, FIXME
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

    return {"image_url": emb.image.url, "search_log_id": search_log.id}


@app.patch("/rating/{search_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def rating(
    search_log_id: int,
    score: Annotated[int, Field(ge=0, le=1)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    res = await db.exec(select(SearchLog).where(SearchLog.id == search_log_id))

    search_log = res.one_or_none()
    if not search_log:
        raise HTTPException(status_code=404, detail="Search log not found")

    search_log.user_rating = score
    db.add(search_log)
    await db.commit()
