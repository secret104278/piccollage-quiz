from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

from cassandra.cluster import Session


def insert_search_event(
    session: Session, search_term: str, event_time: Optional[datetime] = None
):
    if event_time is None:
        event_time = datetime.now()

    session.execute(
        "INSERT INTO sticker_search.search_events (search_term, event_time) VALUES (%s, %s)",
        (search_term, event_time),
    )


def insert_reported_stickers(
    session: Session,
    search_term: str,
    sticker_ids: List[int],
    event_time: Optional[datetime] = None,
):
    if event_time is None:
        event_time = datetime.now()

    session.execute(
        "INSERT INTO sticker_search.reported_search_results (search_term, sticker_ids, event_time) VALUES (%s, %s, %s)",
        (search_term, sticker_ids, event_time),
    )


def get_search_frequencies(session: Session, window_hour: int):
    search_frequencies = {}
    rows = session.execute(
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


def get_reported_sticker_ids(session: Session, window_hour: int):
    reported_sticker_ids = defaultdict(set)
    rows = session.execute(
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
