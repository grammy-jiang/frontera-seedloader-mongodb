import pprint
from ast import literal_eval

from pymongo import MongoClient
from scrapy.utils.test import get_crawler
from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

from frontera_seedloader_mongodb.contrib.scrapy.middlewares.seeds.mongodb import \
    MongoDBAsyncSeedLoader
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

    def tearDown(self):
        self.coll.drop()

    @inlineCallbacks
    def seed_loader_setup(self):
        crawler = get_crawler(settings_dict=self.settings_dict)
        spider = crawler._create_spider(name='foo')
        seed_loader = MongoDBAsyncSeedLoader.from_crawler(crawler)
        yield seed_loader.open_spider(spider)

        return seed_loader

    @inlineCallbacks
    def test_load_seeds(self):
        seed_loader = yield self.seed_loader_setup()
        # seeds = yield seed_loader.load_seeds()
        # print(type(seeds))
        for seed in seed_loader.load_seeds():
        # for seed in seeds:
            _seed = yield seed
            # print(type(_seed))
        #     pp.pprint(_seed)
