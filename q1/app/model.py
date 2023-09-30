from typing import Dict, List

from pydantic import BaseModel


class StickerSearchRequest(BaseModel):
    search_term: str


class StickerSearchResponse(BaseModel):
    sticker_ids: List[int]


class StickerReportRequest(BaseModel):
    search_term: str
    sticker_ids: List[int]


class StickerReportResponse(BaseModel):
    success: bool


class StickerFeedbackResponse(BaseModel):
    search_frequencies: Dict[str, int]
    reported_sticker_ids: Dict[str, List[int]]
