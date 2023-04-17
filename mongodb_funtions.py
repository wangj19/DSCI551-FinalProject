from pymongo import MongoClient
import validators
import json
import uuid
import random

command_list = ["GET", "PUT", "POST", "PATCH", "DELETE"]
filter_conds_list = ["orderBy", "limitToFirst",
                     "limitToLast", "equalTo", "startAt", "endAt"]


# helper function -- input a dict and a path/list of keys, return the value corresponding to the path/list of keys in the list
def dict_keys_helper(dict_, keys):
    if not isinstance(dict_, dict):
        return dict_
    output = dict_
    for key in keys:
        if key in list(output.keys()):
            temp = output[key]
            output = temp
    return output

# helper function -- help GET command to product appropriate output of filter condition


def filter_process(content, condition_query):
    orderBy = condition_query["orderBy"]
    limitValue = condition_query["limitValue"]
    startAt = condition_query["startAt"]
    endAt = condition_query["endAt"]
    equalTo = condition_query["equalTo"]
    output = []
    if content is None:
        return content
    elif isinstance(content, dict):
        for item in content.items():
            document = {item[0]: item[1]}
            output.append(document)
    elif not hasattr(content, '__iter__'):
        return content
    else:
        output = content

    # process filter without orderby condition
    if orderBy is None:
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    # process orderby $key
    # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='$Key'"
    elif orderBy.lower() == "$key":
        output = sorted(output, key=lambda x: list(x.keys())[0])
        # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='$Key'&equalTo='0987654321'"
        if equalTo is not None:
            temp = [document for document in output if list(document.keys())[
                0] == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if list(document.keys())[
                0] >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if list(document.keys())[
                0] <= endAt]
            output = temp
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    # process orderby $value
    # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='$value'
    elif orderBy.lower() == "$value":
        can_sort = []
        non_sort = []
        for x in output:
            if isinstance(x[list(x.keys())[0]], dict) or x[list(x.keys())[0]] is None:
                non_sort.append(x)
            else:
                can_sort.append(x)
        can_sort = sorted(can_sort, key=lambda x: x[list(x.keys())[0]])
        output = can_sort
        if equalTo is not None:
            temp = [document for document in output if document[list(document.keys())[
                0]] == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if document[list(document.keys())[
                0]] >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if document[list(document.keys())[
                0]] <= endAt]
            output = temp
        output += non_sort
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    # handle filter orderby a specific key or path of keys
    # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='price'&endAt=30&limitToLast=3"
    else:
        can_sort = []
        non_sort = []
        paths = orderBy.split("/")
        for x in output:
            if isinstance(x[list(x.keys())[0]], dict):
                existFlag = True
                temp = x[list(x.keys())[0]]
                for p in paths:
                    if not isinstance(temp, dict):
                        existFlag = False
                        break
                    if p in list(temp.keys()):
                        temp = temp[p]
                        print(temp)
                    else:
                        existFlag = False
                        break
                if isinstance(temp, dict):
                    existFlag = False

                if existFlag:
                    can_sort.append(x)
                else:
                    non_sort.append(x)
            else:
                non_sort.append(x)
        can_sort = sorted(can_sort, key=lambda x: dict_keys_helper(
            x[list(x.keys())[0]], paths))
        output = can_sort
        if equalTo is not None:
            temp = [document for document in output if dict_keys_helper(
                document[list(document.keys())[0]], paths) == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if dict_keys_helper(
                document[list(document.keys())[0]], paths) >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if dict_keys_helper(
                document[list(document.keys())[0]], paths) <= endAt]
            output = temp
        output += non_sort
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    output_dict = dict()
    for document in output:
        output_dict.update(document)

    return output_dict


# Currently can do get command without filter
def process_GET(url, conditions):

    # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='price'&limitToFirst=5"
    # Process filter conditions for GET command
    orderByIndex = None
    startValue = None
    endValue = None
    equalValue = None
    limitOrder = 0
    limitToNumber = None
    current_cond_key = []
    condition_query = dict({"orderBy": orderByIndex, "limitValue": limitToNumber, "startAt": startValue,
                            "endAt": endValue, "equalTo": equalValue})
    if conditions is not None:
        for cond in conditions.split("&"):
            # check if the filter format is valid
            if len(cond.split("=")) < 2:
                return "Invalid Command: inproper filter condition format"
            filter_key = cond.split("=")[0]
            filter_value = cond.split("=")[1]
            # check if the filter condition is valid
            if filter_key not in filter_conds_list:
                return "Invalid Command: invalid filter condition"
            # check if the filter condition is duplicated
            if filter_key in current_cond_key:
                return "Invalid Command: duplicated filter condition"
            else:
                current_cond_key.append(filter_key)

            # adjust filter_value to corresponding type
            if (filter_value[0] == "\'" and filter_value[-1] == "\'") or (filter_value[0] == "\"" and filter_value[-1] == "\""):
                filter_value = filter_value[1:-1]
            elif filter_value.lower() == "true":
                filter_value = True
            elif filter_value.lower() == "false":
                filter_value = False
            elif "." in filter_value:
                filter_value = float(filter_value)
            else:
                filter_value = int(filter_value)

            # start to handle filter conditions
            if filter_key == "orderBy":
                orderByIndex = filter_value
                condition_query.update({"orderBy": orderByIndex})
            elif filter_key == "limitToFirst":
                if limitOrder < 0:
                    return "Invalid Command: cannot enter limitToFirst and limitToLast together"
                elif not isinstance(filter_value, int):
                    return "Invalid Command: limitToFirst only accepts integer"
                else:
                    limitOrder = 1
                    limitToNumber = filter_value
                    condition_query.update(
                        {"limitValue": limitOrder * limitToNumber})
            elif filter_key == "limitToLast":
                if limitOrder > 0:
                    return "Invalid Command: cannot enter limitToFirst and limitToFirst together"
                elif not isinstance(filter_value, int):
                    return "Invalid Command: limitToLast only accepts integer"
                else:
                    limitOrder = -1
                    limitToNumber = filter_value
                    condition_query.update(
                        {"limitValue": limitOrder * limitToNumber})
            elif filter_key == "startAt":
                startValue = filter_value
                condition_query.update({"startAt": startValue})
            elif filter_key == "endAt":
                endValue = filter_value
                condition_query.update({"endAt": endValue})
            elif filter_key == "equalTo":
                equalValue = filter_value
                condition_query.update({"equalTo": equalValue})
            else:
                return "Invalid Command: invalid filter condition"

            # print(filter_key)
            # print(filter_value)

    # Get address and port to establish connection to mongodb
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017
    # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='price'&limitToFirst=5"

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))
    if len(parsed_url) == 1:
        # only enter localhost or IP address end with .json -- invalid url form
        # untested code -- currently unreachable
        output = dict()
        for db_name in client.list_database_names():
            db_content = dict()
            print(db_name)
            db = client[db_name]
            for col_name in db.list_collection_names():
                col_content = dict()
                for document in db[col_name].find({}, {"_id": 0}):
                    col_content.update(document)
                db_content.update({col_name: col_content})
            output.update({db_name: db_content})
        return output

    elif len(parsed_url) == 2:
        # Input the IP address and empty database name, return entire MongoDB
        # curl -X GET "http://localhost:27017/.json"
        if parsed_url[1] == "":
            output = dict()
            for db_name in client.list_database_names():
                db_content = dict()
                db = client[db_name]
                for col_name in db.list_collection_names():
                    col_content = dict()

                    for document in db[col_name].find({}, {"_id": 0}):
                        col_content.update(document)
                    db_content.update({col_name: col_content})
                output.update({db_name: db_content})
            return filter_process(output, condition_query)
        # input the IP address and database name, return entire database
        # curl -X GET "http://localhost:27017/DSCI551.json"
        else:
            db_content = dict()
            db = client[parsed_url[1]]
            for col_name in db.list_collection_names():
                col_content = dict()
                for document in db[col_name].find({}, {"_id": 0}):
                    col_content.update(document)
                    # print(document)
                db_content.update({col_name: col_content})
            output = dict({parsed_url[1]: db_content})
            return filter_process(output, condition_query)
    # input IP address, database name, and collection name, return entire collection
    # curl -X GET "http://localhost:27017/DSCI551/books.json"
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        content = []
        for document in db[parsed_url[2]].find({}, {"_id": 0}):
            content.append(document)
        return filter_process(content, condition_query)
    # curl -X GET "http://localhost:27017/DSCI551/books/1234567890.json"
    # curl -X GET "http://localhost:27017/DSCI551/books/1234567890/price.json"
    else:
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        content = None
        documents = dict()
        for document in db[parsed_url[2]].find({}, {"_id": 0}):
            documents.update(document)
        item = documents
        for key in json_keys:
            if type(item) == dict:
                if key in list(item.keys()):
                    temp = item[key]
                    item = temp
                else:
                    item = None
                    break
            else:
                item = None
                break
        if item is not None:
            content = item
        
        # return content
        return filter_process(content, condition_query)


def process_DELETE(url):
    # Get address and port to establish connection to mongodb
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017
    # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='price'&limitToFirst=5"

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))
    if len(parsed_url) == 1:
        # only enter localhost or IP address end with .json -- invalid url form
        # untested code -- currently unreachable
        # http://localhost:27017.json would be identified as invalid json
        return "Whole MongoDB DELETE"

    elif len(parsed_url) == 2:
        if parsed_url[1] == "":
            return "DELETE Entire mongoDB: currently suspend"
        # curl -X DELETE "http://localhost:27017/test.json"
        else:
            client.drop_database(parsed_url[1])
    # curl -X DELETE "http://localhost:27017/test/test.json"
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        db.drop_collection(parsed_url[2])
    # curl -X DELETE "http://localhost:27017/test/test/1234567890.json"
    elif len(parsed_url) == 4:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        primary_key = parsed_url[3]
        collection.delete_one({primary_key: {'$exists': True}})
    # curl -X DELETE "http://localhost:27017/test/test/1234567890/price.json"
    else:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        primary_key = parsed_url[3]
        to_remove = primary_key
        for k in parsed_url[4:]:
            to_remove = to_remove + "." + k
        print(to_remove)
        collection.update_one({primary_key: {'$exists': True}}, {
                              '$unset': {f'{to_remove}': 1}})
    return "DELETE http://" + url + ".json"


def process_PUT(url, data):
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))

    js = dict()
    if data[0] != "\'" or data[-1]!="\'":
        return "Invalid Command: Please enter data in single quotation marks"
    else:
        js = json.loads(data[1:-1])
        print(js)
    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))
    # curl -X PUT "http://localhost:27017/test/test.json" -d '{"1234577777":{"name":"John"}}' -- PASS
    # curl -X PUT "http://localhost:27017/test/test.json" -d '{"1234577777":{"name":"Hugo"}}' -- PASS
    # curl -X PUT "http://localhost:27017/test/test/1234577777.json" -d '{"name":"John"}' -- PASS
    # curl -X PUT "http://localhost:27017/test/test/1234577777/name.json" -d '{"name":"John"}' -- PASS
    # curl -X PUT "http://localhost:27017/test/test/1234577777/name/a/b.json" -d '{"name":"John"}' -- PASS
    if len(parsed_url) < 3:
        return "Invalid Command: invalid POST on database or Collection"
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        if len(list(js.keys()))!=1:
            return "Invalid Command: inappropriate json data input. Please enter one item with primary key for PUT"
        id = list(js.keys())[0]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)
        ## if document id exist already: do update_one
        if id in list(documents.keys()):
            collection.update_one({id: {"$exists": True}}, {"$set": js})
        ## else: do insert_ones
        else:
            collection.insert_one(js)
    else:
        document_id = parsed_url[3]
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)

        # document id (the fourth object in the command) exists in the existing data, 
        # post item on the existing documents
        if document_id in list(documents.keys()):
            # get existing document 
            dataToUpdate = dict({document_id: documents[document_id]})
            if len(json_keys)>1:
                dataToUpdate = recursive_helper(dataToUpdate, json_keys, js, True)
            else:
                dataToUpdate[document_id].update(js)
            newValue = {"$set": dataToUpdate}
            filter = {document_id: {"$exists": True}}
            # print(newValue)
            collection.update_one(filter, newValue)
        # document id doesnt exist in the existing data,
        # post item by creating new document and all the fields in front of it
        else:
            item = js
            for key in reversed(json_keys):
                temp = dict()
                temp.update({key:item})
                item = temp
            # print(item)
            collection.insert_one(item)

    
    return 'PUT ' + str(js) + " into http://" + url + ".json"



# This is a recursive helper function used for POST PUT and PATCH,
# Input: data - original data in json format which need to update
#        keys - paths to the points need to be replaced
#        js   - json format data which is used to replace
#        flag - flag to check wheck this is a valid path existing in original data,
#               if the path is no more exists in original data, the function would create
#               it to put the js(to_update part)
# Output: json format data which is updated from data by js on the corresponding paths(keys)
def recursive_helper(data, keys, js, flag):
    if len(keys) == 0:
        return js
    elif flag:
        if keys[0] in list(data.keys()):
            if type(data[keys[0]]) is not dict:
                data.update({keys[0]:recursive_helper(data, keys[1:], js, False)})
            else:
                data[keys[0]].update(recursive_helper(data[keys[0]], keys[1:], js, flag))
            return data
        else:
            temp = {keys[0]:recursive_helper(data, keys[1:], js, False)}
            return temp
    else:
        temp = {keys[0]:recursive_helper(data, keys[1:], js, flag)}
        return temp
        


# FINISH
# Since it's hard to change name of collection/database or create new collection/database,
# we currently limit the length of command is greater than or equal to 3 items,
# Assume that all database and collection entered is existing and available 
def process_POST(url, data):
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017
    js = dict()
    if data[0] != "\'" or data[-1]!="\'":
        return "Invalid Command: Please enter data in single quotation marks"
    else:
        js = json.loads(data[1:-1])
        myuuid = str(uuid.uuid4().hex)
        js = dict({myuuid: js})
    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))
    if len(parsed_url) < 3:
        return "Invalid Command: invalid POST on database or Collection"
    
    # curl -X POST "http://localhost:27017/test/test.json" -d '{"name":"John"}'
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        collection.insert_one(js)
    # curl -X POST "http://localhost:27017/test/test/1234577777.json" -d '{"name":"John"}'
    # curl -X POST "http://localhost:27017/test/test/1234577777/name.json" -d '{"name":"John"}'
    # curl -X POST "http://localhost:27017/test/test/1234577777/name/a/b.json" -d '{"name":"John"}'
    else:
        document_id = parsed_url[3]
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)

        # document id (the fourth object in the command) exists in the existing data, 
        # post item on the existing documents
        if document_id in list(documents.keys()):
            # get existing document 
            dataToUpdate = dict({document_id: documents[document_id]})
            if len(json_keys)>1:
                dataToUpdate = recursive_helper(dataToUpdate, json_keys, js, True)
            else:
                dataToUpdate[document_id].update(js)
            newValue = {"$set": dataToUpdate}
            filter = {document_id: {"$exists": True}}
            # print(newValue)
            collection.update_one(filter, newValue)
        # document id doesnt exist in the existing data,
        # post item by creating new document and all the fields in front of it
        else:
            item = js
            for key in reversed(json_keys):
                temp = dict()
                temp.update({key:item})
                item = temp
            # print(item)
            collection.insert_one(item)
        return "POST " + str(dict({myuuid:js[myuuid]})) + " to http://" + url + ".json"
        

# this function will help us create a new ISBN / Primary Key number for a new book.
def generate_random_number(existing_keys):
    while True:
        existing_keys_set = set(existing_keys)  # Convert dict_keys to a set for faster lookup
        # Generate a new 10-digit random number
        new_key = random.randint(10**9, 10**10-1)
        # Check if the new random number is not in the existing keys
        if new_key not in existing_keys_set:
            # If the new random number is unique, return it
            return int(new_key)
def process_PATCH(url, data):
    # Parse the data we get from client
    # curl -X PATCH "http://localhost:27017/DSCI551/books/1234567890.json"
    # (curl -X PATCH -d '{"name": "John Smith", "age": 25}' 'https://inf551-1b578.firebaseio.com/users/100.json')
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017

    # curl -X PATCH "http://localhost:27017/DSCI551/books/1491957660.json" -d '{"name":"Mybook123","author":"[JamesSusanto]","Price":55,"description":"testing book patch"}'
    if data[0] != "\'" or data[-1] != "\'":
        return "Invalid Command: Please enter data in single quotation marks"
    else:
        formatted_data = json.loads(data[1:-1])
        print(formatted_data)
        # newID = str(uuid.uuid4().hex)
        # formatted_data = dict({newID: formatted_data})

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"

    # Establish a connection to MongoDB using the provided URL
    # (similar to what you did in the process_GET function)
    client = MongoClient(address, int(port))

    if len(parsed_url) < 3:
        return "Invalid Command: invalid POST on database or Collection"
    elif len(parsed_url) == 3:
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)

        # check if the user inserted an existing ISBN or not.
        # If it exists, use the existing ID and make new ID if it does not exist
        print(type(list(documents.keys())[0]))
        if len(list(formatted_data.keys())) != 1:
            id = generate_random_number(documents.keys())
        else:
            id = list(formatted_data.keys())[0]

        ## if document id exist already: do update_one
        if id in list(documents.keys()):
            collection.update_one({id: {"$exists": True}}, {"$set": formatted_data})
        ## else: do insert_ones
        else:
            collection.insert_one(formatted_data)
    else:
        document_id = parsed_url[3]
        json_keys = parsed_url[3:]
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        documents = dict()
        # Find a document with the primary_key field present
        for document in collection.find({}, {"_id": 0}):
            documents.update(document)

        # Check if the data you want to update exists in the database
        # You can use the find_one() method to search for a document
        # matching the conditions provided in the URL
        # If the data exists, update the data
        # Use the update_one() method with the conditions and payload as arguments
        # document id (the fourth object in the command) exists in the existing data,
        # post item on the existing documents
        if document_id in list(documents.keys()):
            # get existing document
            dataToUpdate = dict({document_id: documents[document_id]})
            if len(json_keys) > 1:
                dataToUpdate = recursive_helper(dataToUpdate, json_keys, formatted_data, True)
            else:
                dataToUpdate[document_id].update(formatted_data)
            newValue = {"$set": dataToUpdate}
            filter = {document_id: {"$exists": True}}
            # print(newValue)
            # Update the document with the provided data
            collection.update_one(filter, newValue)
        # document id doesn't exist in the existing data,
        # post item by creating new document and all the fields in front of it
        else:
            item = formatted_data
            for key in reversed(json_keys):
                temp = dict()
                temp.update({key: item})
                item = temp
            # print(item)
            # If the data does not exist, insert the new data
            collection.insert_one(item)

    return "PATCH " + str(formatted_data) + " to http://" + url + ".json"


# High-level function for command processing


def command_process(command):
    try:
        # parse command by spaces
        # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='price'&limitToFirst=5"
        parsed_command = command.split(" ")
        print(parsed_command)
        # check if the command starts with "curl"
        if parsed_command[0].lower() != "curl":
            return "Invalid Command: only accept curl command"

        # check if the second element is "-X"
        if parsed_command[1].lower() != "-x":
            return "Invalid Command: invalid option, please enter \"-X\" option"

        # check if the command is in [GET, , PUT, POST, PATCH, DELETE]
        if parsed_command[2].upper() not in command_list:
            return "Invalid Command: only accept GET, , PUT, POST, PATCH, DELETE command"

        # check if the url is entered in parenthesis and is a valid url format
        if not ((parsed_command[3][0] == "\'" and parsed_command[3][-1] == "\'") or (parsed_command[3][0] == "\"" and parsed_command[3][-1] == "\"")):
            return "Invalid Command: please enter url with parenthesis"
        if not validators.url(parsed_command[3][1:-2]):
            return "Invalid Command: " + parsed_command[3] + " is invalid url"

        # further parse the command and identify the filter conditions in the url
        url = parsed_command[3][1:-1]
        db_url = url.split("?")[0]
        filter_conditions = None
        if len(url.split("?")) == 2:
            filter_conditions = url.split("?")[1]
        elif len(url.split("?")) > 2:
            return "Invalid Command: Inproper format of filter conditions"

        # check if the db url starts with http:// and ends with .json
        if db_url[0:7] != "http://" or db_url[-5:] != ".json":
            return "Invalid Command: enter url starts with \'http://\' and ends with \'.json\'"

        # Start real processing and connect to Mongodb
        # process GET with conditions
        if parsed_command[2].upper() == "GET":
            return process_GET(db_url[7:-5], filter_conditions)

        # process POST
        elif parsed_command[2].upper() == "POST":
            if parsed_command[3] == '-d':
                process_POST(db_url[7:-5], parsed_command[4])
            elif parsed_command[4] == '-d':
                return process_POST(db_url[7:-5], parsed_command[5])
            else:
                return "invalid command please enter a url with -d"
        elif parsed_command[2].upper() == "PUT":
            if parsed_command[3] == '-d':
                process_PUT(db_url[7:-5], parsed_command[4])
            elif parsed_command[4] == '-d':
                return process_PUT(db_url[7:-5], parsed_command[5])
            else:
                return "invalid command please enter a url with -d"
        elif parsed_command[2].upper() == "PATCH":
            # If data does not exist, InsertOne. if data exist, updateOne.
            # check if there is -d for data insertion,
            # always check if after -d there is "'{"
            # check key, because key must be STRING and no need to check value because it can be anything
            # TODO: handle post command
            if parsed_command[3] == '-d':
                process_PATCH(db_url[7:-5], parsed_command[4])
            elif parsed_command[4] == '-d':
                return process_PATCH(db_url[7:-5], parsed_command[5])
            else:
                return "invalid command please enter a url with -d"
        elif parsed_command[2].upper() == "DELETE":
            # TODO: handle post command
            print("DELETE")
            return process_DELETE(db_url[7:-5])
        return parsed_command
    except Exception as e:
        print("Invalid Command:", str(e))
        return "Invalid Command: " + str(e)
