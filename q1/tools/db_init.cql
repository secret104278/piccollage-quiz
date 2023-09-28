CREATE KEYSPACE IF NOT EXISTS sticker_search
    WITH REPLICATION = { 
        'class' : 'SimpleStrategy', 
        'replication_factor' : 1 
    };

CREATE TABLE IF NOT EXISTS sticker_search.search_events (
    search_term TEXT,
    event_time TIMESTAMP,
    PRIMARY KEY (search_term, event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);

CREATE TABLE IF NOT EXISTS sticker_search.reported_search_results (
    search_term TEXT,
    sticker_ids LIST<INT>,
    event_time TIMESTAMP,
    PRIMARY KEY (search_term, event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);

