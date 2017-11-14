import logging
import pprint
from typing import Generator

from bson import DEFAULT_CODEC_OPTIONS
from frontera import Settings
from frontera.contrib.scrapy.middlewares.seeds import SeedLoader
from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.signals import spider_closed
from scrapy.signals import spider_opened
from scrapy.spiders import Spider
from twisted.internet.defer import inlineCallbacks, Deferred
from txmongo.connection import ConnectionPool

from .....settings.default_settings import SEEDS_MONGODB_COLLECTION
from .....settings.default_settings import SEEDS_MONGODB_DATABASE
from .....utils.get_mongodb_uri import get_mongodb_uri

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


class MongoDBAsyncSeedLoader(SeedLoader):
    def configure(self, settings: Settings):
        self.settings = self.crawler.settings
        self.uri = get_mongodb_uri(self.settings)
        self.codec_options = DEFAULT_CODEC_OPTIONS.with_options(
            unicode_decode_error_handler='ignore')

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        obj = cls(crawler)
        crawler.signals.connect(obj.open_spider, signal=spider_opened)
        crawler.signals.connect(obj.close_spider, signal=spider_closed)
        return obj

    @inlineCallbacks
    def open_spider(self, spider: Spider):
        self.cnx = yield ConnectionPool(
            self.uri,
            codec_options=self.codec_options)
        self.db = yield getattr(
            self.cnx,
            self.settings.get(SEEDS_MONGODB_DATABASE, 'seeds'))
        self.coll = yield getattr(
            self.db,
            self.settings.get(SEEDS_MONGODB_COLLECTION, 'seeds'))

        yield self.coll.with_options(codec_options=self.codec_options)

        logger.info('Spider opened: Open the connection to MongoDB: %s',
                    self.uri)

    @inlineCallbacks
    def close_spider(self, spider: Spider):
        yield self.cnx.disconnect()
        logger.info('Spider closed: Close the connection to MongoDB %s',
                    self.uri)

    def process_start_requests(
            self,
            start_requests,
            spider: Spider) -> Generator[Request, None, None]:
        spider.start_urls = self.load_seeds
        yield from spider.start_requests()

    @inlineCallbacks
    def load_seeds(self, dfr: Deferred = None):
        if not dfr:
            docs, dfr = yield self.coll.find_with_cursor(
                # **self.settings.get(SEEDS_MONGODB_SEEDS_QUERY, {'filter': {}})
                cursor=True
            )
            return docs, dfr
        else:
            docs, dfr = yield dfr
            return docs, dfr
            # while docs:
            #     for doc in docs:
            #         yield doc
            #     else:
            #         docs, dfr = yield dfr
