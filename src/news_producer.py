import re
import atoma
import requests
import logging
from dataclasses import dataclass
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO)

@dataclass(frozen=True)
class News:
    _id: str
    title: str
    link: str
    published: str
    description: str
    author: str
    language: str

    def as_dict(self):
        return self.__dict__

class NewsProducer:
    def __init__(self, rss_feed, language):
        self.rss_feed = rss_feed
        self.language = language
        self.formatter = NewsFormatter(language)

    def _fetch_rss_feed(self, proxies):
        try:
            response = requests.get(self.rss_feed, proxies=proxies)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logging.error(f"Error fetching RSS feed: {e}")
            return None

    def _parse_rss_feed(self, rss_feed_content):
        try:
            return atoma.parse_rss_bytes(rss_feed_content)
        except atoma.exceptions.FeedXMLError as e:
            logging.error(f"XML Parsing Error: {e}")
            return None

    def get_news_stream(self, proxies):
        rss_feed_content = self._fetch_rss_feed(proxies)
        if rss_feed_content:
            rss_feed = self._parse_rss_feed(rss_feed_content)
            if rss_feed is not None:
                for entry in rss_feed.items:
                    formatted_entry = self.formatter.format_entry(entry)
                    yield formatted_entry
            else:
                logging.error("Failed to parse RSS feed.")
        else:
            logging.error("Failed to retrieve RSS feed content.")

class NewsFormatter:
    def __init__(self, language):
        self.language = language
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.id_regex = "[^0-9a-zA-Z_-]+"
        self.default_author = "Unknown"

    def format_entry(self, entry):
        description = self.format_description(entry)
        return News(
            _id=self.construct_id(entry.title),
            title=entry.title,
            link=entry.link,
            published=self.unify_date(entry),
            description=description,
            author=self.assign_author(entry.author),
            language=self.language
        )

    def construct_id(self, title):
        return re.sub(self.id_regex, "", title).lower()

    def unify_date(self, entry):
        # Essayez d'obtenir la date de publication
        date = getattr(entry, 'published', getattr(entry, 'pubDate', None))

        # Si la date est présente, formatez-la
        if date and hasattr(date, 'strftime'):
            return date.strftime(self.date_format)

        # Si la date n'est pas disponible, utilisez la date/heure actuelle
        return datetime.now().strftime(self.date_format)

    def assign_author(self, author):
        return self.default_author if not author or not hasattr(author, 'name') else author.name

    def format_description(self, entry):
        description = re.sub("<.*?>", "", entry.description) if entry.description else ""
        return description[:1000]