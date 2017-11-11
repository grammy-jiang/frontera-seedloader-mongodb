from scrapy.settings import Settings

from ..settings.default_settings import SEEDS_MONGODB_DATABASE
from ..settings.default_settings import SEEDS_MONGODB_HOST
from ..settings.default_settings import SEEDS_MONGODB_OPTIONS_
from ..settings.default_settings import SEEDS_MONGODB_PASSWORD
from ..settings.default_settings import SEEDS_MONGODB_PORT
from ..settings.default_settings import SEEDS_MONGODB_USERNAME


def get_mongodb_uri(settings: Settings) -> str:
    return 'mongodb://{account}{path}{options}'.format(
        account=_gen_mongo_account(settings),
        path=_gen_mongo_path(settings),
        options=_gen_mongo_option(settings))


def _gen_mongo_account(settings: Settings) -> str:
    return {
        True: '{username}:{password}@'.format(
            username=settings.get(SEEDS_MONGODB_USERNAME),
            password=settings.get(SEEDS_MONGODB_PASSWORD)),
        False: ''
    }.get(all(map(settings.get, [SEEDS_MONGODB_USERNAME, SEEDS_MONGODB_PASSWORD])))


def _gen_mongo_path(settings: Settings) -> str:
    return '{host}:{port}/{database}'.format(
        host=settings.get(SEEDS_MONGODB_HOST, 'localhost'),
        port=settings.get(SEEDS_MONGODB_PORT, 27017),
        database=settings.get(SEEDS_MONGODB_DATABASE, 'seeds'))


def _gen_mongo_option(settings: Settings) -> str:
    options = list(filter(
        lambda x: all([x[0].startswith(SEEDS_MONGODB_OPTIONS_),
                       x[0].replace(SEEDS_MONGODB_OPTIONS_, '')]),
        settings.attributes.items()
    ))
    if options:
        return '?{options}'.format(
            options='&'.join(map(
                lambda x: '{option}={value}'.format(
                    option=x[0].replace(SEEDS_MONGODB_OPTIONS_, '').lower(),
                    value=x[1]),
                options)))
    else:
        return ''
