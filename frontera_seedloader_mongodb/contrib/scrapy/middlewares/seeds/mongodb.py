import logging
from itertools import starmap, chain

from bson import DEFAULT_CODEC_OPTIONS
from frontera.contrib.scrapy.middlewares.seeds import SeedLoader
from frontera.exceptions import NotConfigured
from pymongo import MongoClient
from pymongo.cursor import Cursor
from scrapy.crawler import Crawler
from scrapy.http import Request
from scrapy.settings import Settings
from scrapy.signals import spider_closed
from scrapy.signals import spider_opened
from scrapy.spiders import Spider
from scrapy.utils.misc import load_object

from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_COLLECTION
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_DATABASE
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_SEEDS_BATCH_SIZE
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_SEEDS_PREPARE
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_SEEDS_QUERY
from frontera_seedloader_mongodb.utils.get_mongodb_uri import get_mongodb_uri

logger = logging.getLogger(__name__)


class MongoDBSeedLoader(SeedLoader):
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

    def open_spider(self, spider: Spider):
        try:
            if self.settings.get(SEEDS_MONGODB_SEEDS_PREPARE):
                self.prepare = load_object(
                    self.settings.get(SEEDS_MONGODB_SEEDS_PREPARE))
            else:
                self.prepare = lambda x: map(lambda y: (y, x), x['websites'])
        except:
            raise NotConfigured

        self.cnx = MongoClient(self.uri)
        self.db = self.cnx.get_database(
            self.settings.get(SEEDS_MONGODB_DATABASE, 'seeds'))
        self.coll = self.db.get_collection(
            self.settings.get(SEEDS_MONGODB_COLLECTION, 'seeds'))

        logger.info('Spider opened: Open the connection to MongoDB: %s',
                    self.uri)

    def close_spider(self, spider: Spider):
        self.cnx.close()
        logger.info('Spider closed: Close the connection to MongoDB %s',
                    self.uri)

    def process_start_requests(self, start_requests, spider: Spider):
        yield from starmap(
            lambda x, y: Request(url=x, meta={'seed': y}),
            chain(*map(self.prepare, self.load_seeds())))

    def load_seeds(self) -> Cursor:
        logger.info(
            'There are %d seeds.',
            self.coll.count(
                self.settings.get(
                    SEEDS_MONGODB_SEEDS_QUERY, {}
                ).get('filter')
            ))
        return self.coll.find(
            **self.settings.get(SEEDS_MONGODB_SEEDS_QUERY, {})
        ).batch_size(
            self.settings.get(SEEDS_MONGODB_SEEDS_BATCH_SIZE, 100)
        )
