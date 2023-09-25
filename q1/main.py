import torch
from fastapi import FastAPI
from pydantic import BaseModel

from q1.imagesearch import ImageSearch


class StickerSearchRequest(BaseModel):
    search_term: str


class StickerSearchResponse(BaseModel):
    sticker_ids: list[int]


class StickerReportRequest(BaseModel):
    search_term: str
    sticker_id: int


class StickerReportResponse(BaseModel):
    success: bool


class StickerFeedbackResponse(BaseModel):
    pass


app = FastAPI()
image_vectors = torch.load("image_vectors.pt")
search = ImageSearch(image_vectors, "cuda" if torch.cuda.is_available() else "cpu")


@app.post("/sticker/search")
async def sticker_search(sticker_search: StickerSearchRequest) -> StickerSearchResponse:
    return StickerSearchResponse(
        sticker_ids=search(sticker_search.search_term).tolist()
    )


@app.post("/sticker/report")
async def sticker_report(report: StickerReportRequest) -> StickerReportResponse:
    """
    For user to report a sticker that is not relevant to the search term.
    """
    return StickerReportResponse(success=True)


@app.get("/sticker/feedback")
async def sticker_feedback() -> StickerFeedbackResponse:
    """
    For admin to get feedback statistic from users.
    """
    return StickerFeedbackResponse()
