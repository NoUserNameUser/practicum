from pymongo import MongoClient

class db_api(object):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = client['FiSher']

    def get_user_by_name(self, uname):
        table = self.db['users']
        table.find()


