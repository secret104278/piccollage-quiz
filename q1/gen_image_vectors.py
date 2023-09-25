from pathlib import Path

import clip
import torch
from PIL import Image
from tqdm import tqdm

if __name__ == "__main__":
    model, preprocess = clip.load("ViT-B/32")

    def get_vector_for_image(image):
        return model.encode_image(preprocess(image).unsqueeze(0))

    image_vectors = torch.cat(
        [
            get_vector_for_image(Image.open(fp))
            for fp in tqdm(list(Path("data/val2014").glob("*.jpg")))
        ]
    )

    torch.save(image_vectors, "image_vectors.pt")
