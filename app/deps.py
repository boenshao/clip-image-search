from collections.abc import AsyncGenerator

import numpy as np
import torch
from sqlmodel.ext.asyncio.session import AsyncSession
from transformers import AutoTokenizer, CLIPTextModelWithProjection

from app.core.db import engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


class CLIPText:
    def __init__(self) -> None:
        self.model = CLIPTextModelWithProjection.from_pretrained(
            "openai/clip-vit-base-patch32"
        )
        self.tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")

    def __call__(self, query: str) -> np.ndarray:
        inputs = self.tokenizer([query], padding=True, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        text_embeds = outputs.text_embeds / outputs.text_embeds.norm(
            p=2, dim=-1, keepdim=True
        )

        return text_embeds.detach().numpy()


clip_text: CLIPText | None = None


def get_clip_text_model() -> CLIPText:
    global clip_text  # noqa: PLW0603
    clip_text = clip_text or CLIPText()
    return clip_text
