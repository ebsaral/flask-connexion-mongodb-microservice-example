from pymongo import MongoClient

PORT = 5000
DEBUG = True
DEFAULT_PAGE_LIMIT = 5
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB_NAME = "ebs"
MONGO_COLLECTION_NAME = "events"
MONGO_CLIENT = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
