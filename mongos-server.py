from pymongo import MongoClient
from flask import Flask, jsonify, request, redirect, url_for, render_template, session
from flask_socketio import SocketIO, emit

# define app
app = Flask(__name__)
async_mode = None
socket_ = SocketIO(app, async_mode=async_mode)
# connect to local MongoDB instance
client = MongoClient('localhost', 27017)
db = client['DSCI551']

# get list of collections in database
collections = db.list_collection_names()

# display list of collections
print("Collections in database 'DSCI551':")
for collection in collections:
    print(collection)

@app.route('/')
def index():
    # display list of collections
    toReturn = "Collections in database 'DSCI551':\n"
    # print("Collections in database 'DSCI551':")
    for collection in collections:
        # print(collection)
        toReturn = toReturn + str(collection) + "/\n"
    return render_template("index.html", collection = toReturn, async_mode = socket_.async_mode)
    
@app.route('/admin')
def hello_admin():
   return render_template("admin.html", async_mode = socket_.async_mode)
@socket_.on("command", namespace="/admin")
def handle_command(command):
    print(command)


# run app
if __name__ == '__main__':
   socket_.run(app, debug=True)
