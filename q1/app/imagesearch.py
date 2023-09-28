from typing import Union

import clip
import numpy as np
import torch


class ImageSearch:
    def __init__(self, image_vectors: np.ndarray, device: Union[str, torch.device]):
        self.image_vectors = image_vectors
        self.model, _ = clip.load("ViT-B/32", device=device)

    def _encode_text(self, text: str) -> torch.Tensor:
        return self.model.encode_text(clip.tokenize(text))

    def __call__(self, text: str) -> torch.Tensor:
        scores = self.image_vectors @ self._encode_text(text).t()
        return scores.squeeze().argsort(descending=True)[:10]
