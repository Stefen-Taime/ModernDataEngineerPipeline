import os
import logging
import redis
from kafka import KafkaProducer

class Config:
    def __init__(self):
        self.setup_logging()
        self.kafka_config = self.load_kafka_config()
        self.redis_config = self.load_redis_config()
        self.my_class_instance = self.MyClass()
        self.test_redis_connection()
        self.test_kafka_connection()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_kafka_config(self):
        kafka_config = {
            'bootstrap_servers': 'localhost:9092',
            'session_timeout_ms': '45000'
        }
        self.logger.info('Kafka configuration set.')
        return kafka_config

    def load_redis_config(self):
        redis_config = {
            "host": 'redis-xxxxxx.cloud.redislabs.com',
            "port": 17135,
            "password": '',
            "username": 'default',
            "db": 0
        }
        self.logger.info('Redis configuration set.')
        return redis_config

    def test_redis_connection(self):
        try:
            r = redis.Redis(**self.redis_config)
            r.ping()
            self.logger.info('Connexion à Redis réussie.')
        except redis.ConnectionError as e:
            self.logger.error(f'Échec de la connexion à Redis : {e}')
            raise

    def test_kafka_connection(self):
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.kafka_config['bootstrap_servers']
            )
            self.logger.info('Connexion à Kafka réussie.')
        except Exception as e:
            self.logger.error(f'Échec de la connexion à Kafka : {e}')
            raise



    @property
    def BOOTSTRAP_SERVERS(self):
        return self.kafka_config.get('bootstrap.servers').split(',')

    @property
    def SECURITY_PROTOCOL(self):
        return self.kafka_config.get('security.protocol')

    @property
    def SASL_MECHANISMS(self):
        return self.kafka_config.get('sasl.mechanisms')

    @property
    def SASL_USERNAME(self):
        return self.kafka_config.get('sasl.username')

    @property
    def SASL_PASSWORD(self):
        return self.kafka_config.get('sasl.password')

    @property
    def SESSION_TIMEOUT_MS(self):
        return int(self.kafka_config.get('session.timeout.ms', 45000))

    @property
    def REDIS_CONFIG(self):
        return self.redis_config

    @property
    def REDIS_KEY(self):
        return os.environ.get('REDIS_KEY', 'proxies')

    @property
    def PROXY_WEBPAGE(self):
        return os.environ.get('PROXY_WEBPAGE', 'https://free-proxy-list.net/')

    @property
    def TESTING_URL(self):
        return os.environ.get('TESTING_URL', 'https://google.com')

    @property
    def MAX_WORKERS(self):
        return int(os.environ.get('MAX_WORKERS', 50))

    @property
    def NUMBER_OF_PROXIES(self):
        return int(os.environ.get('NUMBER_OF_PROXIES', 50))

    @property
    def RSS_FEEDS(self):
        return {
            "en": [
                "https://www.goal.com/feeds/en/news",
                "https://www.eyefootball.com/football_news.xml",
                "https://www.101greatgoals.com/feed/",
                "https://sportslens.com/feed/",
                "https://deadspin.com/rss"
            ],
            "pl": [
                "https://weszlo.com/feed/",
                "https://sportowefakty.wp.pl/rss.xml",
                "https://futbolnews.pl/feed",
                "https://igol.pl/feed/"
            ],
            "es": [
                "https://as.com/rss/tags/ultimas_noticias.xml",
                "https://e00-marca.uecdn.es/rss/futbol/mas-futbol.xml",
                "https://www.futbolred.com/rss-news/liga-de-espana.xml",
                "https://www.futbolya.com/rss/noticias.xml"
            ],
            "de": [
                "https://www.spox.com/pub/rss/sport-media.xml",
                "https://www.dfb.de/news/rss/feed/"
            ]
        }

    class MyClass:
        @property
        def VALIDATOR_CONFIG(self):
            """Documentation des paramètres de configuration"""
            VALIDATOR_CONFIG = {
                "description_length": 100,  # Example value
                "languages": ["en", "fr", "es", "de"]   # Example value
            }
            return VALIDATOR_CONFIG
        
    def _get_int_env_var(self, name, default):
        """Récupère une variable d'environnement comme entier."""
        try:
            return int(os.environ.get(name, default))
        except ValueError:
            raise ValueError(f"La variable d'environnement {name} doit être un entier.")

    def _get_list_env_var(self, name, default):
        """Récupère une variable d'environnement comme liste de chaînes de caractères."""
        value = os.environ.get(name, default)
        # Nettoyer les espaces blancs et convertir en minuscules pour une correspondance cohérente.
        return [lang.strip().lower() for lang in value.split(',')]

# Usage
config = Config()
validator_config = config.my_class_instance.VALIDATOR_CONFIG
print(validator_config)    