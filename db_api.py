from pymongo import MongoClient

class db_api(object):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['FiSher']
        table = self.db['users']
        table.remove({'username':'demo', 'ipaddr':'127.0.0.1'})
        # table.list_indexes()
        result = table.find({'username': 'demo', 'ipaddr': '127.0.0.1'})
        if result.count() == 0:
            print 'no result'
        else:
            print result.count()
        for r in result:
            print r



if __name__ == "__main__":
    db_api()


