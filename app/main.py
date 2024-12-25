from typing import Annotated

import torch
from fastapi import Depends, FastAPI
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from transformers import AutoTokenizer, CLIPTextModelWithProjection

from .deps import get_db
from .models import CLIPEmbedding

model = CLIPTextModelWithProjection.from_pretrained("openai/clip-vit-base-patch32")
tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")


app = FastAPI()


@app.get("/")
async def read_root() -> dict:
    return {"Hello": "World"}


@app.post("/query")
async def read_item(query: str, db: Annotated[AsyncSession, Depends(get_db)]) -> dict:
    inputs = tokenizer([query], padding=True, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    text_embeds = outputs.text_embeds / outputs.text_embeds.norm(
        p=2, dim=-1, keepdim=True
    )
    text_embeds = text_embeds.detach().numpy()

    emb = (
        await db.exec(
            select(CLIPEmbedding)
            .order_by(
                CLIPEmbedding.embedding.max_inner_product(text_embeds[0].tolist())
            )
            .options(selectinload(CLIPEmbedding.image))  # type: ignore
            .limit(1)
        )
    ).one_or_none()

    return {"image_id": emb.image if emb else None}
