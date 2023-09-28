# piccollage-quiz

## Q1
- API to search for a term
- API to report one or more stickers
- API to access feedback
  - search term frequency
  - reported stickers <-> search term

The problem contains two main topics: search and feedback.
- Search: the search part is quite simple and straightforward in this use case which is mostly handled by `ImageSearch`, the potential bottleneck is `(image_vectors @ encoded_text).argsort()` which might be replaced by a vector database such as [Milvus](https://github.com/milvus-io/milvus) in the future.

- Feedback: the feedback part is a common scenario for data driven projects, which may involved different systems and engineers to build up a comprehensive solution. I will list some possible solutions and discussion here, and chose a simplified version from them as my final implementation.

### Background
The feedback data is time-series data. The write is very heavy, but the read is seldom, and probably will be queried by a offline cronjob. The data is not very sensitive, which means we can tolerate some data loss. The data volume may be huge over time, so we need to consider the scalability.

### relation database
Use a MySQL or PostgreSQL to record the feedback events. We can schedule a daily cronjob to aggregate the events and store as CSV at s3, or run on-demain query as API call depends on the real use case. If we have a master-slave setup, we can do the query on slave to reduce the load on master.
This solution is simple and easy to implement, but it might not be scalable when the data grows. 

### redis
We can use redis hashset to store the access frequency of each search term, and use set to store the reported stickers. 
This solution is simple and easy to implement, but most of the data of events is not accessed frequently, which might be a waste. Besides, redis only support simple data modeling, for example, the approach here might require a full redis scan to retrieve all the reported stickers, which is not efficient to be maintained when other features share the same redis cluster. Also, we usually want to partition the aggregated data by timestamp (probably by day) to extract increment, which is not supported by redis.

### cassandra
Cassandra is designed to handle write heavy time-series data, which might be a good fit for this use case. We can use the search term as the partition key, and the timestamp as the clustering key. However, by doing so, all nodes will need to be accessed while running aggregation query. Besides, cassandra doesn't support complex query compared to big data tools such as spark SQL, which might be a problem when we want to do more complex aggregation in the future.

### data warehouse (kafka + hive + spark sql + s3)
This is a complex but highly scalable and flexible solution, which is also the tech stack I've work with while working at Houzz. The server can sequentially write the event to a local file, where a log watcher will further push this events to kafka. The log aggregator will consume the events from kafka and write to s3 in parquet and hive. The data scientist will then schedule hourly/daily cronjob to run spark SQL to aggregate the data further to produce useful metrics. (for example, the search term frequency, the reported stickers, etc.)
This solution might be too complex for this use case, since we don't need to support ad-hoc query and complex ETL pipeline yet.

### Final solution
I use the cassandra solution as my final implementation, since it's simple and easy to implement, and optimized design for write-heavy time serial data.
As for next step improvement, we can use kafka + spark SQL to do the computation and still write aggregated data back to cassandra.
