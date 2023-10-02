# piccollage-quiz

## Q1
- API to search for a term
- API to report one or more stickers
- API to access feedback
  - search term frequency
  - reported stickers <-> search term

The problem contains two main topics: search and feedback. 

### Search
The search part is quite simple and straightforward in this use case, mostly handled by `ImageSearch`. The potential bottleneck is `(image_vectors @ encoded_text).argsort()`, which could potentially be replaced by a vector database like [Milvus](https://github.com/milvus-io/milvus) in the future.

### Feedback
The feedback part is a common scenario for data-driven projects, involving different systems and engineers to build a comprehensive solution. I will list some possible solutions and discuss them here, and choose a simplified version as my final implementation.

#### Background
The feedback data is time-series data. The write operations are very heavy, but the read operations are infrequent and will probably be queried by an offline cron job. The data is not very sensitive, meaning we can tolerate some data loss. The data volume may become huge over time, so scalability needs to be considered.

#### Solution - Relational Database
Using MySQL or PostgreSQL to record the feedback events is one option. We can schedule a daily cron job to aggregate the events and store them as CSV files in S3, or run on-demand queries as API calls depending on the real use case. If we have a master-slave setup, we can perform the query on the slave to reduce the load on the master.

This solution is simple and easy to implement, but it might not be scalable when the data grows. Although there are tools like `sqoop` to transfer data from MySQL to Hadoop to solve the query scalability problem, relational databases are not ideal for write-heavy time-series data since they are primarily designed for OLTP use cases.

#### Solution - Redis
We can use Redis hashsets to store the access frequency of each search term and sets to store the reported stickers.

This solution is simple and easy to implement, but most of the event data is not accessed frequently, which could be a waste of memory. Additionally, Redis only supports simple data modeling. For example, the approach here might require a full Redis scan to retrieve all the reported stickers, which is not efficient to maintain when other features share the same Redis cluster. Also, we usually want to partition the aggregated data by timestamp (probably by day) to extract increments, which is not directly supported by Redis (setup TTL may solve this partially, but will cause data lose once the job fail over the dealine).

Redis could be a better candidate if we only want to reply with the top N search terms to the user.

#### Solution - Cassandra
Cassandra is designed to handle write-heavy time-series data, making it a good fit for this use case. We can use the search term as the partition key and the timestamp as the clustering key.

However, by doing so, all nodes will need to be accessed while running aggregation queries. Additionally, Cassandra doesn't support complex queries compared to big data tools like Spark SQL, which becomes a problem when we want to perform more complex aggregations.

#### Solution - Data Warehouse (Kafka + Hive + Spark SQL + S3)
This is a complex but highly scalable and flexible solution, which is also the tech stack I've worked with while at Houzz.

The servers sequentially write the events to local files, where a log tailer will further push these events to Kafka. The events will be written directly to a `raw_event` table, and there will be another PySpark job to perform basic aggregation and write to S3 in Parquet format and Hive. Data scientists can then schedule hourly/daily cron jobs to run Spark SQL and further aggregate the data to produce useful metrics (e.g., search term frequency, reported stickers, etc.).

In a real production environment, we can use multiple cloud services to perform these tasks. For example, we can use GCP Pub/Sub to publish the events from the backend, then use GCP Dataflow to aggregate and write to BigQuery or directly write raw events to BigQuery. We can schedule another cron job to run Spark SQL and perform aggregation, writing to another BigQuery table, and kick off the ML data pipeline to train the model.

#### Final implementation
I have chosen the Cassandra solution as my implementation here since it's easy to set up locally and is optimized for write-heavy time-series data.
