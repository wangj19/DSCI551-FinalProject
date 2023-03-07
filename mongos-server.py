from pymongo import MongoClient

# connect to local MongoDB instance
client = MongoClient('localhost', 27017)
db = client['DSCI551']

# get list of collections in database
collections = db.list_collection_names()

# display list of collections
print("Collections in database 'DSCI551':")
for collection in collections:
    print(collection)
