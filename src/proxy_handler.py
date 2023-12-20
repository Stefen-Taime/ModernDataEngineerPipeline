import redis
import random
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import logging
from config import Config
from datetime import timedelta

# Configuration et variables globales
config = Config()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_CONFIG = {
    'host': config.REDIS_CONFIG['host'],
    'port': config.REDIS_CONFIG['port'],
    'db': config.REDIS_CONFIG['db'],
    'username': config.REDIS_CONFIG['username'],
    'password': config.REDIS_CONFIG['password'],
    'decode_responses': True
}
REDIS_KEY = 'proxypool'
PROXY_WEBPAGE = config.PROXY_WEBPAGE
TESTING_URL = config.TESTING_URL
MAX_WORKERS = config.MAX_WORKERS
PROXY_EXPIRATION = timedelta(minutes=5)


headers_list = [
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate", 
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
        "Dnt": "1", 
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
        "X-Amzn-Trace-Id": "Root=1-5ee7bae0-82260c065baf5ad7f0b3a3e3"
    },
    {
        "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.reddit.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }   
]

class ProxyHandler:
    def __init__(self):
        self.redis_client = redis.Redis(**REDIS_CONFIG)

    def get_proxies(self):
        if self.redis_client.exists(REDIS_KEY):
            proxies = self.redis_client.lrange(REDIS_KEY, 0, -1)
            expiration = self.redis_client.ttl(REDIS_KEY)
            if expiration == -1:
                self.redis_client.expire(REDIS_KEY, PROXY_EXPIRATION)
            elif expiration < PROXY_EXPIRATION.total_seconds():
                self.redis_client.delete(REDIS_KEY)
                proxies = []
        else:
            proxies = []
        if not proxies:
            self.update_proxy_pool()
            proxies = self.redis_client.lrange(REDIS_KEY, 0, -1)
        return proxies

    def update_proxy_pool(self):
        headers = random.choice(headers_list)
        page = requests.get(PROXY_WEBPAGE, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        proxies = []
        for row in soup.find('tbody').find_all('tr'):
            proxy = row.find_all('td')[0].text + ':' + row.find_all('td')[1].text
            proxies.append(proxy)
        self.redis_client.rpush(REDIS_KEY, *proxies)
        self.redis_client.expire(REDIS_KEY, PROXY_EXPIRATION)

    def test_proxy(self, proxies):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(self.test_single_proxy, proxies))
        valid_proxies = [proxy for valid, proxy in zip(results, proxies) if valid]
        self.redis_client.delete(REDIS_KEY)
        self.redis_client.rpush(REDIS_KEY, *valid_proxies)

    def test_single_proxy(self, proxy):
        headers = random.choice(headers_list)
        try:
            resp = requests.get(TESTING_URL, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=3)
            if resp.status_code == 200:
                return True
        except:
            pass
        return False
class ProxyHandler:
    def __init__(self):
        self.redis_client = redis.Redis(**REDIS_CONFIG)

    def get_proxies(self):
        if self.redis_client.exists(REDIS_KEY):
            proxies = self.redis_client.lrange(REDIS_KEY, 0, -1)
            expiration = self.redis_client.ttl(REDIS_KEY)
            if expiration == -1:
                self.redis_client.expire(REDIS_KEY, PROXY_EXPIRATION)
            elif expiration < PROXY_EXPIRATION.total_seconds():
                self.redis_client.delete(REDIS_KEY)
                proxies = []
        else:
            proxies = []
        if not proxies:
            self.update_proxy_pool()
            proxies = self.redis_client.lrange(REDIS_KEY, 0, -1)
        return proxies

    def update_proxy_pool(self):
        headers = random.choice(headers_list)
        page = requests.get(PROXY_WEBPAGE, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        proxies = []
        for row in soup.find('tbody').find_all('tr'):
            proxy = row.find_all('td')[0].text + ':' + row.find_all('td')[1].text
            proxies.append(proxy)
        self.redis_client.rpush(REDIS_KEY, *proxies)
        self.redis_client.expire(REDIS_KEY, PROXY_EXPIRATION)

    def test_proxy(self, proxies):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(self.test_single_proxy, proxies))
        valid_proxies = [proxy for valid, proxy in zip(results, proxies) if valid]
        if valid_proxies:
            self.redis_client.delete(REDIS_KEY)
            self.redis_client.rpush(REDIS_KEY, *valid_proxies)
        else:
            logger.info("No valid proxies found.")


    def test_single_proxy(self, proxy):
        headers = random.choice(headers_list)
        try:
            resp = requests.get(TESTING_URL, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=3)
            if resp.status_code == 200:
                return True
        except:
            pass
        return False

if __name__ == "__main__":
    try:
        proxy_handler = ProxyHandler()
        proxies = proxy_handler.get_proxies()
        proxy_handler.test_proxy(proxies)
        logger.info(f"Retrieved and validated {len(proxies)} proxies.")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")