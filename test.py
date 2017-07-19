# from communication import *
#
# print passphrase_gen(6);

from pymongo import MongoClient

client = MongoClient('localhost', 27017)

print client.database_names()
db = client['test-db']
print db.collection_names()
for i in db['test-collection'].find({
    'a':"a"
}):
    print i
# collection = db['test-collection']
# test = {
#     "a": "1",
#     "b": "2",
#     "c": "3",
#     "d": "4",
# }
# collection.insert_one(test)
