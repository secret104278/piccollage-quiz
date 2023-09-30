import asyncio
import os

import torch
from cassandra.cluster import Cluster
from fastapi import FastAPI

from .db import (
    get_reported_sticker_ids,
    get_search_frequencies,
    insert_reported_stickers,
    insert_search_event,
)
from .imagesearch import ImageSearch
from .model import (
    StickerFeedbackResponse,
    StickerReportRequest,
    StickerReportResponse,
    StickerSearchResponse,
)

cassandra_session = Cluster(
    [os.getenv("CASSANDRA_HOST")], os.getenv("CASSANDRA_PORT")
).connect()
app = FastAPI()
search = ImageSearch(
    torch.load(os.getenv("IMAGE_VECTORS_PATH", "image_vectors.pt")),
    "cuda" if torch.cuda.is_available() else "cpu",
)


@app.get("/sticker/search")
async def sticker_search(search_term: str) -> StickerSearchResponse:
    await insert_search_event(cassandra_session, search_term)

    return StickerSearchResponse(sticker_ids=search(search_term).tolist())


@app.post("/sticker/report")
async def sticker_report(report: StickerReportRequest) -> StickerReportResponse:
    """
    For user to report a sticker that is not relevant to the search term.
    I assume user can only report a bad sticker.
    """
    await insert_reported_stickers(
        cassandra_session, report.search_term, report.sticker_ids
    )

    return StickerReportResponse(success=True)


@app.get("/sticker/feedback")
async def sticker_feedback(window_hour: int) -> StickerFeedbackResponse:
    """
    For admin to get feedback statistic from users.
    """
    search_frequencies, reported_sticker_ids = await asyncio.gather(
        get_search_frequencies(cassandra_session, window_hour),
        get_reported_sticker_ids(cassandra_session, window_hour),
    )

    return StickerFeedbackResponse(
        search_frequencies=search_frequencies, reported_sticker_ids=reported_sticker_ids
    )


@app.get("/healthcheck")
async def healthcheck() -> bool:
    return True
