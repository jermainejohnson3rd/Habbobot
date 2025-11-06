from sqlitedict import SqliteDict

class DbUtil():
    
    def __init__(self, dbname, tablename) -> None:
       self.db = SqliteDict(dbname, tablename=tablename, autocommit=True)
       
    def insert_user(self, user : dict, name=None):
        if name is None:
            self.db[user['name']] = {'channels' : user['channels'],
							 'status' : user['status']}
        else:
            self.db[name] = user
    
    def get_user(self, name):
        try:
            return self.db[name]
        except KeyError:
            return None
        
    def cleanup_user(self, name):
        try:
            self.db.pop(name)
        except KeyError:
            pass
    
    def get_length(self):
        return len(self.db)
    
    def clean_channel(self, channelid):
        try:
            for item in self.db.items():
                if channelid in item[1]['channels']:
                    item[1]['channels'].remove(channelid)
                self.insert_user(item[1], item[0])
                print(channelid)
        except KeyError:
            pass
    
                    
