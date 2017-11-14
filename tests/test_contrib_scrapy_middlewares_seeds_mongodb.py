import pprint
from ast import literal_eval
from unittest import TestCase

from pymongo import MongoClient
from pymongo.cursor import Cursor
from scrapy.http import Request
from scrapy.utils.test import get_crawler

from frontera_seedloader_mongodb.contrib.scrapy.middlewares.seeds.mongodb import \
    MongoDBSeedLoader
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_COLLECTION
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_DATABASE
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_HOST
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_PORT
from frontera_seedloader_mongodb.settings.default_settings import \
    SEEDS_MONGODB_SEEDS_QUERY
from tests import get_testdata_generator

pp = pprint.PrettyPrinter(indent=4)


class TestFileSeedLoader(TestCase):
    settings_dict = {
        # SEEDS_MONGODB_USERNAME: '',
        # SEEDS_MONGODB_PASSWORD: '',
        SEEDS_MONGODB_HOST: 'localhost',
        SEEDS_MONGODB_PORT: 27017,
        SEEDS_MONGODB_DATABASE: 'seeds',
        SEEDS_MONGODB_COLLECTION: 'seeds',
        # SEEDS_MONGODB_OPTIONS_: ''
        SEEDS_MONGODB_SEEDS_QUERY: {},
    }

    def setUp(self):
        self.cnx = MongoClient()
        self.db = self.cnx.get_database(
            self.settings_dict[SEEDS_MONGODB_DATABASE])
        self.coll = self.db.get_collection(
            self.settings_dict[SEEDS_MONGODB_COLLECTION])

        self.list_docs = list(map(
            literal_eval,
            get_testdata_generator('sample_companies')))
        self.coll.insert_many(self.list_docs)

        self.crawler = get_crawler(settings_dict=self.settings_dict)
        self.spider = self.crawler._create_spider(name='foo')
        self.seed_loader = MongoDBSeedLoader.from_crawler(self.crawler)
        self.seed_loader.open_spider(self.spider)

    def tearDown(self):
        self.coll.drop()
        self.cnx.close()
        self.seed_loader.close_spider(self.spider)

    def test_load_seeds(self):
        seeds = self.seed_loader.load_seeds()
        self.assertIsInstance(seeds, Cursor)
        for seed in seeds:
            self.assertIn(seed, self.list_docs)

    def test_process_start_requests(self):
        for request in self.seed_loader.process_start_requests(
                None, self.spider):
            self.assertIsInstance(request, Request)
            doc = self.coll.find_one({'websites': request.url})
            self.assertIn(request.url, doc['websites'])
            self.assertDictEqual(request.meta['seed'], doc)
