from pymongo import MongoClient
from flask import Flask, jsonify, request, redirect, url_for

# define app
app = Flask(__name__)
# connect to local MongoDB instance
client = MongoClient('localhost', 27017)
db = client['DSCI551']

# get list of collections in database
collections = db.list_collection_names()

# display list of collections
print("Collections in database 'DSCI551':")
for collection in collections:
    print(collection)

@app.route('/',defaults={'myPath': ''})
def homePage(myPath):
    # display list of collections
    toReturn = "Collections in database 'DSCI551':\n"
    print("Collections in database 'DSCI551':")
    for collection in collections:
        print(collection)
        toReturn = toReturn + str(collection) + "\n"
    return toReturn
    
@app.route('/admin')
def hello_admin():
   return 'Hello Admin'

# run app
if __name__ == '__main__':
   app.run(debug = True)
