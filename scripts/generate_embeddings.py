import pathlib
import pickle

import torch
from PIL import Image
from transformers import CLIPImageProcessor, CLIPVisionModelWithProjection


def main() -> None:
    # Load pre-trained CLIP model and processor, only the image part is needed
    model = CLIPVisionModelWithProjection.from_pretrained(
        "openai/clip-vit-base-patch32"
    )
    processor = CLIPImageProcessor.from_pretrained("openai/clip-vit-base-patch32")

    paths = list(pathlib.Path("temp/val2014/").glob("*.jpg"))
    images = [Image.open(p) for p in paths]
    inputs = processor(images=images, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    # normalize, so later we can do dot product for consine similarity
    image_embeds = outputs.image_embeds / outputs.image_embeds.norm(
        p=2, dim=-1, keepdim=True
    )
    image_embeds = image_embeds.detach().numpy()

    # ! In the real world
    # ! pickle is not a good format for serlizaing any kind of data
    # ! there's lots of better alternatives in terms of speed and security
    # ! like msgpack, avro, parquet, etc...
    # ! but I don't want to introduce dependency just for the sake of this offline task.
    # ! I can use JSON, but that will make my git repo bloat
    # ! (I'm a bit mysophobia, I don't like bug file in my repo... XD)
    # ! I'll just use pickle for now, for demo purposes
    with pathlib.Path("data/embeddings.pickle").open("wb") as f:
        pickle.dump(
            [(path.name, image_embeds[i].tolist()) for i, path in enumerate(paths)],
            f,
        )


if __name__ == "__main__":
    main()
