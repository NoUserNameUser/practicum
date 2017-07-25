# from communication import *
#
# print passphrase_gen(6);

from pymongo import MongoClient
import datetime


client = MongoClient('localhost', 27017)

print client.database_names()
db = client['FiSher']
print db.collection_names()
# db['users'].remove()
results = db['users'].find()
for r in results:
    print r


# print datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")