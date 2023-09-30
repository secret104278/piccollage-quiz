import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial
from typing import List, Optional

from cassandra.cluster import ResponseFuture, Session


async def execute_future(session: Session, *args, **kwargs):
    # FIXME: args and kwargs have no type hints

    loop = asyncio.get_event_loop()

    cassandra_fut: ResponseFuture = await loop.run_in_executor(
        None, partial(session.execute_async, *args, **kwargs)
    )

    future = loop.create_future()

    def result_cb(result):
        if future.cancelled():
            return
        future.get_loop().call_soon_threadsafe(future.set_result, result)

    def exception_cb(exeption):
        if future.cancelled():
            return
        future.get_loop().call_soon_threadsafe(future.set_exception, exeption)

    cassandra_fut.add_callbacks(callback=result_cb, errback=exception_cb)

    return await future


async def insert_search_event(
    session: Session, search_term: str, event_time: Optional[datetime] = None
):
    if event_time is None:
        event_time = datetime.now()

    return await execute_future(
        session,
        "INSERT INTO sticker_search.search_events (search_term, event_time) VALUES (%s, %s)",
        (search_term, event_time),
    )


async def insert_reported_stickers(
    session: Session,
    search_term: str,
    sticker_ids: List[int],
    event_time: Optional[datetime] = None,
):
    if event_time is None:
        event_time = datetime.now()

    return await execute_future(
        session,
        "INSERT INTO sticker_search.reported_search_results (search_term, sticker_ids, event_time) VALUES (%s, %s, %s)",
        (search_term, sticker_ids, event_time),
    )


async def get_search_frequencies(session: Session, window_hour: int):
    search_frequencies = {}
    rows = await execute_future(
        session,
        """\
SELECT search_term, COUNT(*) AS search_frequency \
FROM sticker_search.search_events \
WHERE event_time > %s \
GROUP BY search_term \
ALLOW FILTERING;""",
        (datetime.now() - timedelta(hours=window_hour),),
    )

    for row in rows:
        search_frequencies[row.search_term] = row.search_frequency
    return search_frequencies


async def get_reported_sticker_ids(session: Session, window_hour: int):
    reported_sticker_ids = defaultdict(set)
    rows = await execute_future(
        session,
        """\
SELECT search_term, sticker_ids \
FROM sticker_search.reported_search_results \
WHERE event_time > %s \
ALLOW FILTERING;""",
        (datetime.now() - timedelta(hours=window_hour),),
    )
    for row in rows:
        reported_sticker_ids[row.search_term].update(row.sticker_ids)
    return reported_sticker_ids
