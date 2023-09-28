import os
from typing import Dict, List

import torch
from cassandra.cluster import Cluster
from fastapi import FastAPI
from pydantic import BaseModel

from .cassandra_utils import (
    get_reported_sticker_ids,
    get_search_frequencies,
    insert_reported_stickers,
    insert_search_event,
)
from .imagesearch import ImageSearch


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


cassandra_session = Cluster(
    [os.getenv("CASSANDRA_HOST")], os.getenv("CASSANDRA_PORT")
).connect()
app = FastAPI()
image_vectors = torch.load(os.getenv("IMAGE_VECTORS_PATH", "image_vectors.pt"))
search = ImageSearch(image_vectors, "cuda" if torch.cuda.is_available() else "cpu")


@app.get("/sticker/search")
async def sticker_search(search_term: str) -> StickerSearchResponse:
    insert_search_event(cassandra_session, search_term)

    return StickerSearchResponse(sticker_ids=search(search_term).tolist())


@app.post("/sticker/report")
async def sticker_report(report: StickerReportRequest) -> StickerReportResponse:
    """
    For user to report a sticker that is not relevant to the search term.
    I assume user can only report a bad sticker.
    """
    insert_reported_stickers(cassandra_session, report.search_term, report.sticker_ids)

    return StickerReportResponse(success=True)


@app.get("/sticker/feedback")
async def sticker_feedback(window_hour: int) -> StickerFeedbackResponse:
    """
    For admin to get feedback statistic from users.
    """
    search_frequencies = get_search_frequencies(cassandra_session, window_hour)
    reported_sticker_ids = get_reported_sticker_ids(cassandra_session, window_hour)

    return StickerFeedbackResponse(
        search_frequencies=search_frequencies, reported_sticker_ids=reported_sticker_ids
    )


@app.get("/healthcheck")
async def healthcheck() -> bool:
    return True
