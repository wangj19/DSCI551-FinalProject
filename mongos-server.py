from pymongo import MongoClient
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit

# define app
app = Flask(__name__, template_folder="templates", static_folder = "statics")
async_mode = None
socket_ = SocketIO(app, async_mode=async_mode)
# connect to local MongoDB instance
client = MongoClient('localhost', 27017)
db = client['DSCI551']

# get list of collections in database
collections = db.list_collection_names()

def command_process(command):
    parsed_command = command.split(" ")
    print(parsed_command)
    if parsed_command[0].lower() != "curl":
        return "Invalid Command: only accept curl command"
    return parsed_command

@app.route('/')
def index():
    # display list of collections
    toReturn = "Collections in database 'DSCI551':\n"
    # print("Collections in database 'DSCI551':")
    for collection in collections:
        # print(collection)
        toReturn = toReturn + str(collection) + "/\n"
    return render_template("index.html", collection = toReturn, async_mode = socket_.async_mode)
@app.route("/login")
def login_page():
    return render_template("login.html", async_mode = socket_.async_mode)

@app.route('/admin', methods = ["GET","POST"])
def admin_page():
   return render_template("admin.html", async_mode = socket_.async_mode)

@app.route("/handle_command", methods=["POST"])
def handle_command():
    command = request.form["command"]
    results = command_process(command)
    return(str(results))

# run app
if __name__ == '__main__':
   socket_.run(app, debug=True)
