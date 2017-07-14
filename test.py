# from communication import *
#
# print passphrase_gen(6);

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['test-db']
collection = db['test-collection']
test = {
    "a": "1",
    "b": "2",
    "c": "3",
    "d": "4",
}
collection.insert_one(test)
