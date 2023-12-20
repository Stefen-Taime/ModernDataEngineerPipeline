
from news_producer import NewsProducer
import redis
from kafka import KafkaProducer
import json
from config import Config
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(), logging.FileHandler('rss_feed.log')])
logger = logging.getLogger(__name__)

# Initialize configuration
config = Config()

def get_proxy(redis_client):
    all_proxies = redis_client.lrange('proxypool', 0, -1)
    return random.choice(all_proxies).decode('utf-8') if all_proxies else None

def produce_entry(producer, topic, news_entry, redis_client):
    try:
        if not redis_client.sismember('published_articles', news_entry._id):
            news_dict = vars(news_entry)
            producer.send(topic, value=news_dict).get(timeout=10)
            logger.info(f"Entry produced successfully: {news_entry.title}")
            redis_client.sadd('published_articles', news_entry._id)
        else:
            logger.info(f"Entry skipped (already published): {news_entry.title}")
    except Exception as e:
        logger.error(f"Error producing entry: {e}")

        logger.error(f"Error producing entry: {e}")




def fetch_and_send_rss_feed():
    redis_client = redis.Redis(**config.redis_config)
    producer = KafkaProducer(
        bootstrap_servers=config.kafka_config['bootstrap_servers'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        for language, feeds in config.RSS_FEEDS.items():
            for feed_url in feeds:
                proxy = get_proxy(redis_client)
                if proxy:
                    news_producer = NewsProducer(feed_url, language)
                    for news_entry in news_producer.get_news_stream({'http': f'http://{proxy}'}):
                        produce_entry(producer, 'Kafka_Topic_A', news_entry, redis_client)
                else:
                    logger.error(f'No proxy available for fetching feed: {feed_url}')
    finally:
        producer.close()
        redis_client.close()
        logger.info('Finished processing all feeds')


if __name__ == "__main__":
    fetch_and_send_rss_feed()
