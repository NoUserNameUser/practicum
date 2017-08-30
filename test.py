# from communication import *
#
# print passphrase_gen(6);

from pymongo import MongoClient
import datetime


client = MongoClient('localhost', 27017)

print client.database_names()
db = client['FiSher']
print db.collection_names()

usertable = db['users']
groupstable = db['share_groups']

# new_group = {
#     '_id': 345678,
#     'owner': 1234321,
#     'name': 'the dreams',
#     'members': [],
#     'files':[],
#     'share_phrase':[],
#     'created':datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
# }
# groupstable.insert(new_group)
# groupstable.update_one({'_id':123456}, {'$set':{'name': 'the pretties'}})

# update user data
# db['users'].update_one({'_id': 1234321}, {'$push':{'share_groups':345678}})


# usertable.remove()
# groupstable.remove()

results = usertable.find()
print "-------------------- users --------------------"
for r in results:
    print r

results = groupstable.find()
print "-------------------- groups --------------------"
for r in results:
    print r



# print datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")