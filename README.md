
## ModernDataEngineering: Building a Robust Data Pipeline: Integrating Proxy Rotation, Kafka, MongoDB, Redis, Logstash, Elasticsearch, and MinIO for Efficient Web Scraping

![](https://cdn-images-1.medium.com/max/4798/1*4ksPu_a3QmlbLPllzWCzDQ.png)

## Utilizing Proxies and User-Agent Rotation

Proxies and Rotating User Agents: To overcome anti-scraping measures, our system uses a combination of proxies and rotating user agents. Proxies mask the scraper’s IP address, making it difficult for websites to detect and block them. Additionally, rotating user-agent strings further disguises the scraper, simulating requests from different browsers and devices.

![](https://cdn-images-1.medium.com/max/3584/1*yTURWK2B-njpZQe5bn9f_Q.png)

Storing Proxies in Redis: Valid proxies are crucial for uninterrupted scraping. Our system stores and manages these proxies in a Redis database. Redis, known for its high performance, acts as an efficient, in-memory data store for managing our proxy pool. This setup allows quick access and updating of proxy lists, ensuring that our scraping agents always have access to working proxies.

## RSS Feed Extraction and Kafka Integration

Extracting News from RSS Feeds: The system is configured to extract news from various RSS feeds. RSS, a web feed that allows users and applications to access updates to websites in a standardized, computer-readable format, is an excellent source for automated news aggregation.

![](https://cdn-images-1.medium.com/max/3584/1*JMhYat6-F_kdgDu_W7VBfQ.png)

Quality Validation and Kafka Integration: Once the news is extracted, its quality is validated. The validated news data is then published to a Kafka topic (Kafka A). Kafka, a distributed streaming platform, is used here for its ability to handle high-throughput data feeds, ensuring efficient and reliable data transfer.

![](https://cdn-images-1.medium.com/max/3766/1*erncyv8oCYHl7SD6NiPYhw.png)

## Data Flow and Storage

MongoDB Integration with Kafka Connect: Kafka Connect Mongo Sink consumes data from Kafka topic A and stores it in MongoDB.

![](https://cdn-images-1.medium.com/max/3726/1*Jl2Q4s2KhW45-_xg5VVE_g.png)

MongoDB, a NoSQL database, is ideal for handling large volumes of unstructured data. The upsert functionality, based on the _id field, ensures that the data in MongoDB is current and avoids duplicates.

![](https://cdn-images-1.medium.com/max/2910/1*0yI_HIybyHykCz869hUn8A.png)

Data Accessibility in FastAPI: The collected data in MongoDB is made accessible through FastAPI with OAuth 2.0 authentication, providing secure and efficient access for administrators.

![](https://cdn-images-1.medium.com/max/2770/1*LIv9y1YMzZiqx1aA6_mJ4g.png)

![](https://cdn-images-1.medium.com/max/2736/1*65F9s8dLEDG6nhrZOhq-uA.png)

![](https://cdn-images-1.medium.com/max/2754/1*vO_iSp0_QqkrDNiB-nugaQ.png)

Logstash and Elasticsearch Integration: Logstash monitors MongoDB replica sets for document changes, capturing these as events. These events are then indexed in Elasticsearch, a powerful search and analytics engine. This integration allows for real-time data analysis and quick search capabilities.

![](https://cdn-images-1.medium.com/max/3834/1*0u-c-LswLnoZ4EPqdENJPA.png)

Data Persistence with Kafka Connect S3-Minio Sink: To ensure data persistence, Kafka Connect S3-Minio Sink is employed. It consumes records from Kafka topic A and stores them in MinIO, a high-performance object storage system. This step is crucial for long-term data storage and backup.

![](https://cdn-images-1.medium.com/max/3804/1*VNVJ9rSaTqtY6D_3EySdFw.png)

## Public Data Access and Search

ElasticSearch for Public Search: The data collected and indexed in Elasticsearch is made publicly accessible through FastAPI. This setup allows users to perform fast and efficient searches across the aggregated data.

![](https://cdn-images-1.medium.com/max/2794/1*nx0Ly8VfkCT79LSApo_uwA.png)

Here are some example API calls and their intended functionality:

Basic Request Without Any Parameters:

* Fetches all news items without applying any specific search criteria or language filter.

* Example API Call: GET [http://localhost:8000/api/v1/news/](http://localhost:8000/api/v1/news/)

Search with a General Keyword:

* Searches across multiple fields (like title, description, and author) using a general keyword.

* Example API Call: GET [http://localhost:8000/api/v1/news/?search=Arsenal](http://localhost:8000/api/v1/news/?search=Arsenal)

* This call returns news items where the word “Arsenal” appears in either the title, description, or author.

Search in a Specific Field:

* Targets a specific field for searching with a keyword.

* Example API Call: GET [http://localhost:8000/api/v1/news/?search=title|Milan](http://localhost:8000/api/v1/news/?search=title|Milan)

* Searches for news items where the title contains the word “Milan”.

Filter by Language:

* Filters news items by a specific language.

* Example API Call: GET [http://localhost:8000/api/v1/news/?language=en](http://localhost:8000/api/v1/news/?language=en)

* Returns news items where the language is English ("en").

Combining General Search with Language Filter:

* Performs a general keyword search while also applying a language filter.

* Example API Call: GET [http://localhost:8000/api/v1/news/?search=Arsenal&language=en](http://localhost:8000/api/v1/news/?search=Arsenal&language=en)

* Searches for items containing “Arsenal” in English language articles.

Combining Specific Field Search with Language Filter:

* Combines a specific field search with a language filter.


* Example API Call: GET [http://localhost:8000/api/v1/news/?search=description|defender&language=en](http://localhost:8000/api/v1/news/?search=description|defender&language=en)

* Looks for news items where the description contains “defender” and the language is English.


# ModernDataEngineerPipeline - Startup Guide

This guide provides step-by-step instructions for setting up and running the "ModernDataEngineerPipeline" project.

## Setup Steps

### 1. Clone the Repository

Start by cloning the repository from GitHub:

```bash
git clone https://github.com/Stefen-Taime/ModernDataEngineerPipeline
```

### 2. Navigate to the Project Directory

```bash
cd ModernDataEngineerPipeline
```

### 3. Launch Services with Docker

Use `docker-compose` to build and start the services:

```bash
docker-compose up --build -d
```

### 3.1 Use MongoDB and Redis Clusters

You can use ready-made MongoDB and Redis clusters from MongoAtlas and Redis, or create a free account to get trial clusters. It is also possible to use local MongoDB and Redis clusters by deploying them with Docker.

### 4. Navigate to the `src` Folder

```bash
cd src
```

### 5. Run the Proxy Handler

Execute `proxy_handler.py` to retrieve proxies and store them in Redis:

```bash
python proxy_handler.py
```

### 6. Handle RSS Feeds with Kafka

Use `rss_handler.py` to produce messages towards Kafka:

```bash
python rss_handler.py
```

### 7. Add JSON Sink Connectors

Add the two JSON Sink connectors found in the `connect` folder on Confluent Connect or use the Connect API.

### 8. Launch Logstash

Run Logstash using Docker:

```bash
docker exec -it <container_id> /bin/bash -c "mkdir -p ~/logstash_data && bin/logstash -f pipeline/ingest_pipeline.conf --path.data /usr/share/logstash/logstash_data"
```

### 9. Start the API

Finally, start the API:

```bash
cd api
python main.py
```

---

Follow these steps to set up and run the "ModernDataEngineerPipeline" project.


[Medium](https://github.com/Stefen-Taime/ModernDataEngineerPipeline](https://medium.com/@stefentaime_10958/moderndataengineering-building-a-robust-data-pipeline-integrating-proxy-rotation-kafka-mongodb-9a908d1bd94f)https://medium.com/@stefentaime_10958/moderndataengineering-building-a-robust-data-pipeline-integrating-proxy-rotation-kafka-mongodb-9a908d1bd94f)
