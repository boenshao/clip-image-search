import json
import pathlib

import torch
from PIL import Image
from transformers import CLIPImageProcessor, CLIPVisionModelWithProjection


def main() -> None:
    # Load pre-trained CLIP model and processor
    model = CLIPVisionModelWithProjection.from_pretrained(
        "openai/clip-vit-base-patch32"
    )
    processor = CLIPImageProcessor.from_pretrained("openai/clip-vit-base-patch32")

    paths = list(pathlib.Path("temp/val2014/").glob("*.jpg"))
    images = [Image.open(p) for p in paths]

    # Preprocess inputs
    inputs = processor(images=images, return_tensors="pt")

    # Generate embeddings
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract and normalize image and text embeddings
    image_embeddings = outputs.image_embeds / outputs.image_embeds.norm(
        p=2, dim=-1, keepdim=True
    )
    image_embeddings = image_embeddings.detach().numpy()

    with pathlib.Path("temp/embeddings.json").open("w") as f:
        json.dump(
            {path.name: image_embeddings[i].tolist() for i, path in enumerate(paths)},
            f,
        )


if __name__ == "__main__":
    main()
