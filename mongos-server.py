from pymongo import MongoClient
from flask import Flask, jsonify, request, render_template, abort, make_response
from flask_socketio import SocketIO, emit
import json
import mongodb_funtions as mf
# define app
app = Flask(__name__, template_folder="templates", static_folder="statics")
async_mode = None
socket_ = SocketIO(app, async_mode=async_mode)
# connect to local MongoDB instance
client = MongoClient('localhost', 27017)
db = client['DSCI551']

# get list of collections in database
collections = db.list_collection_names()
books_collection = db["books"]



# Websocket Process
@socket_.on("create")
def handle_create(new_book):
    try:
        # check if the ISBN number alreadys exists or not
        books = dict()
        for book in books_collection.find({}, {"_id": 0}):
            books.update(book)
        isbn = new_book["isbn"]
        name = new_book["title"]
        author = new_book["author"]
        price = new_book["price"]
        description = new_book["description"]
        if isbn in list(books.keys()):
            error_message = "This ISBN number already exists."
            emit("create_fail", error_message)
            return False
        # Do something with the new_book data here
        new_data = {isbn: {"name":name, "author": author, "price": price, 
            "description": description}}
        books_collection.insert_one(new_data)
        emit("book_created", name)
        return True
    
    except Exception as e:
        error_message = str(e)
        emit("create_fail", error_message)
        return False

@socket_.on("delete")
def handle_delete(isbn):
    # Delete the book with the given ISBN from the database
    # Emit a 'book_deleted' event to all connected clients
    try:
        print(isbn)
        books = dict()
        for book in books_collection.find({}, {"_id": 0}):
            books.update(book)
        if isbn not in list(books.keys()):
            error_message = "Invalid ISBN number!"
            emit("delete_fail", error_message)
            return False
        filter = {isbn: {"$exists": True}}
        books_collection.delete_one(filter)
        emit("book_deleted", isbn)
        return True
    except Exception as e:
        error_message = str(e)
        emit("delete_fail", error_message)
        return False

@socket_.on("update")
def handle_update(new):
    # Delete the book with the given ISBN from the database
    # Emit a 'book_updated' event to all connected clients
    try:
        print(new)
        new_book = json.loads(new)
        print(new)
        books = dict()
        for book in books_collection.find({}, {"_id": 0}):
            books.update(book)
        isbn = new_book["isbn"]
        name = new_book["title"]
        author = new_book["author"]
        price = new_book["price"]
        description = new_book["description"]
        if isbn not in list(books.keys()):
            error_message = "Invalid ISBN number!"
            emit("update_fail", error_message)
            return False
        # Do something with the new_book data here
        new_data = {"$set": {isbn: {"name":name, "author": author, "price": price, 
            "description": description}}}
        filter = {isbn: {"$exists": True}}
        books_collection.update_one(filter, new_data)
        emit("book_updated", name)
        return True
    
    except Exception as e:
        error_message = str(e)
        emit("update_fail", error_message)
        return False

@socket_.on("command")
def handle_command_(command):
    print(command)
    output = str(mf.command_process(command))
    # print(output)
    emit("command_output", output)
    return True

@app.route('/')
def index():
    books = books_collection.find({}, {"_id": 0})
    books_data = []
    for book in books:
        data = book[list(book.keys())[0]]
        book_data = dict({"ISBN": str(list(book.keys())[0]), "title": data["name"], "author": data["author"],
                          "price": data["price"], "description": data["description"]})
        books_data.append(book_data)
    return render_template('index.html', books=books_data)

# APP route
@app.route('/book/<isbn>')
def book_detail(isbn):
    document = books_collection.find(
        {str(isbn): {"$exists": True}}, {"_id": 0})
    book_data = {}
    for book in document:
        data = book[list(book.keys())[0]]
        book_data = dict({"ISBN": list(book.keys())[0], "title": data["name"], "author": data["author"],
                          "price": data["price"], "description": data["description"]})
    return render_template("book_detail.html", book_details = book_data)


@app.route("/login")
def login_page():
    return render_template("login.html", async_mode=socket_.async_mode)


@app.route('/admin', methods=["GET", "POST"])
def admin_page():
    return render_template("admin.html", async_mode=socket_.async_mode)


# @app.route("/handle_command")
# def handle_command():
#     command = request.form["command"]
#     results = mf.command_process(command)
#     return str(results)



# HTTP fetch process
# This part is no more used for our APP
# @app.route('/add_book', methods=['POST'])
# def add_book():
#     try:
#         new_book = request.json
#         # check if the ISBN number alreadys exists or not
#         books = dict()
#         for book in books_collection.find({}, {"_id": 0}):
#             books.update(book)
#         isbn = new_book["isbn"]
#         name = new_book["title"]
#         author = new_book["author"]
#         price = new_book["price"]
#         description = new_book["description"]
#         if isbn in list(books.keys()):
#             error_message = "This ISBN number already exists."
#             response = make_response(jsonify({"error": error_message}), 400)
#             return response
#         # Do something with the new_book data here
#         new_data = {isbn: {"name":name, "author": author, "price": price, 
#             "description": description}}
#         books_collection.insert_one(new_data)
#         success_message = "Success!"
#         response = make_response(jsonify({"message": success_message}), 200)
#         return response
    
#     except Exception as e:
#         error_message = str(e)
#         response = make_response(jsonify({"error": error_message}), 400)
#         return response

# @app.route('/update_book', methods=['PUT'])
# def update_book():
#     try:
#         new_book = request.json
#         # check if the ISBN number alreadys exists or not
#         books = dict()
#         for book in books_collection.find({}, {"_id": 0}):
#             books.update(book)
#         isbn = new_book["isbn"]
#         name = new_book["title"]
#         author = new_book["author"]
#         price = new_book["price"]
#         description = new_book["description"]
#         if isbn not in list(books.keys()):
#             error_message = "Invalid ISBN number!"
#             response = make_response(jsonify({"error": error_message}), 400)
#             return response
#         # Do something with the new_book data here
#         new_data = {"$set": {isbn: {"name":name, "author": author, "price": price, 
#             "description": description}}}
#         filter = {isbn: {"$exists": True}}
#         books_collection.update_one(filter, new_data)
#         success_message = "Success!"
#         response = make_response(jsonify({"message": success_message}), 200)
#         return response
    
#     except Exception as e:
#         error_message = str(e)
#         response = make_response(jsonify({"error": error_message}), 400)
#         return response

# @app.route('/delete_book/<isbn>', methods=['DELETE'])
# def delete_book(isbn):
#     try:
#         print(isbn)
#         books = dict()
#         for book in books_collection.find({}, {"_id": 0}):
#             books.update(book)
#         if isbn not in list(books.keys()):
#             error_message = "Invalid ISBN number!"
#             response = make_response(jsonify({"error": error_message}), 400)
#             return response
#         filter = {isbn: {"$exists": True}}
#         books_collection.delete_one(filter)
#         success_message = "Success!"
#         response = make_response(jsonify({"message": success_message}), 200)
#         return response
#     except Exception as e:
#         error_message = str(e)
#         response = make_response(jsonify({"error": error_message}), 400)
#         return response
    
# run app
if __name__ == '__main__':
    socket_.run(app, debug=True)
