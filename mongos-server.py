from pymongo import MongoClient
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
import mongodb_funtions as mf
# define app
app = Flask(__name__, template_folder="templates", static_folder = "statics")
async_mode = None
socket_ = SocketIO(app, async_mode=async_mode)
# connect to local MongoDB instance
client = MongoClient('localhost', 27017)
db = client['DSCI551']

# get list of collections in database
collections = db.list_collection_names()
books_collection = db["books"]
@app.route('/')
def index():

    books = books_collection.find({}, {"_id":0})
    books_data = []
    for book in books:
        data = book[list(book.keys())[0]]
        book_data = dict({"ISBN": list(book.keys())[0], "title": data["name"], "author": data["author"], 
                          "price": data["price"], "description": data["description"]})
        books_data.append(book_data)
    return render_template('index.html', books=books_data)

@app.route('/book/<isbn>')
def book_detail(isbn):
    document = books_collection.find({str(isbn): {"$exists": True}}, {"_id":0})
    book_data = {}
    for book in document:
        data = book[list(book.keys())[0]]
        book_data = dict({"ISBN": list(book.keys())[0], "title": data["name"], "author": data["author"], 
                          "price": data["price"], "description": data["description"]})
    return str(book_data)

@app.route("/login")
def login_page():
    return render_template("login.html", async_mode = socket_.async_mode)

@app.route('/admin', methods = ["GET","POST"])
def admin_page():
   return render_template("admin.html", async_mode = socket_.async_mode)

@app.route("/handle_command", methods=["POST"])
def handle_command():
    command = request.form["command"]
    results = mf.command_process(command)
    return(str(results))

# run app
if __name__ == '__main__':
   socket_.run(app, debug=True)
