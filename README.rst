===========================
Frontera-SeedLoader-MongoDB
===========================

.. image:: https://img.shields.io/pypi/v/frontera-seedloader-mongodb.svg
   :target: https://pypi.python.org/pypi/frontera-seedloader-mongodb
   :alt: PyPI Version

.. image:: https://img.shields.io/travis/grammy-jiang/frontera-seedloader-mongodb/master.svg
   :target: http://travis-ci.org/grammy-jiang/frontera-seedloader-mongodb
   :alt: Build Status

.. image:: https://img.shields.io/badge/wheel-yes-brightgreen.svg
   :target: https://pypi.python.org/pypi/frontera-seedloader-mongodb
   :alt: Wheel Status

.. image:: https://img.shields.io/codecov/c/github/grammy-jiang/frontera-seedloader-mongodb/master.svg
   :target: http://codecov.io/github/grammy-jiang/frontera-seedloader-mongodb?branch=master
   :alt: Coverage report

Overview
========

Frontera is a great framework for broad crawling, especially working with
scrapy. This package provides a seed loader from MongoDB in a async ways for
frontera:

* Querying seeds can be customized

Requirements
============

* Txmongo, a async MongoDB driver with Twisted

* Tests on Python 3.5

* Tests on Linux, but it's a pure python module, should work on other platforms
  with official python and Twisted supported

Installation
============

The quick way::

    pip install frontera-seedloader-mongodb

Or put this middleware just beside the scrapy project.

Documentation
=============

Set Seed Loader in ``SPIDERMIDDLEWARES`` in ``settings.py``, for example::

    # -----------------------------------------------------------------------------
    # FRONTERA SEEDLOADER MONGODB ASYNC
    # -----------------------------------------------------------------------------

    SPIDERMIDDLEWARES.update({
        'frontera_seedloader_mongodb.contrib.scrapy.middlewares.seeds.mongodb.MongoDBAsyncSeedLoader': 500,
    })

    SEEDS_MONGODB_USERNAME = 'user'
    SEEDS_MONGODB_PASSWORD = 'password'
    SEEDS_MONGODB_HOST = 'localhost'
    SEEDS_MONGODB_PORT = 27017
    SEEDS_MONGODB_DATABASE = 'test_mongodb_async_db'
    SEEDS_MONGODB_COLLECTION = 'test_mongodb_async_coll'

    # SEEDS_MONGODB_OPTIONS_ = 'SEEDS_MONGODB_OPTIONS_'

Settings Reference
==================

SEEDS_MONGODB_USERNAME
----------------------

A string of the username of the database.

SEEDS_MONGODB_PASSWORD
----------------------

A string of the password of the database.

SEEDS_MONGODB_HOST
------------------

A string of the ip address or the domain of the database.

SEEDS_MONGODB_PORT
------------------

A int of the port of the database.

SEEDS_MONGODB_DATABASE
----------------------

A string of the name of the database.

SEEDS_MONGODB_COLLECTION
------------------------

A list of the indexes to create on the collection.

SEEDS_MONGODB_OPTIONS_*
-----------------------

Options can be attached when the seed loader start to connect to MongoBD.

If any options are needed, the option can be set with the prefix
``SEEDS_MONGODB_OPTIONS_``, the pipeline will parse it.

For example:

+---------------+-------------------------------------+
| option name   | in ``settings.py``                  |
+---------------+-------------------------------------+
| authMechanism | SEEDS_MONGODB_OPTIONS_authMechanism |
+---------------+-------------------------------------+

For more options, please refer to the page:

* `Connection String URI Format — MongoDB Manual 3.4`_

.. _`Connection String URI Format — MongoDB Manual 3.4`: https://docs.mongodb.com/manual/reference/connection-string/#connections-standard-connection-string-format


SEEDS_MONGODB_SEEDS_QUERY
-------------------------

A dictionary as the keyword arguments to query. The default value is::

   SEEDS_MONGODB_SEEDS_QUERY = {
      'filter': None,
      'projection': None,
      'skip': 0,
      'limit': 0,
      'sort': None
   }

The keys and values in this setting is followed the keyword arguments of the
method ``find_with_cursor`` of the collection in ``txmongo``. Please refer to
the following documents for more details.

* `txmongo package — TxMongo 16.1.0 documentation`_

.. _`txmongo package — TxMongo 16.1.0 documentation`: https://txmongo.readthedocs.io/en/latest/txmongo.html#txmongo.collection.Collection.find_with_cursor

* `collection – Collection level operations — PyMongo 3.5.1 documentation`_

.. _`collection – Collection level operations — PyMongo 3.5.1 documentation`: http://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find

NOTE
====

The database drivers may have different api for the same operation, this
seed loader adopts txmongo as the async driver for MongoDB. If you want to
customize this seed loader, please read the following documents for more
details.

* `Welcome to TxMongo’s documentation!`_

.. _`Welcome to TxMongo’s documentation!`: https://txmongo.readthedocs.io/en/latest/

* `pymongo – Python driver for MongoDB`_

.. _`pymongo – Python driver for MongoDB`: http://api.mongodb.com/python/current/api/pymongo/

TODO
====

* split the MongoDB to backback, make this seed load more flexible
