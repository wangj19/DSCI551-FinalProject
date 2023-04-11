from pymongo import MongoClient
import validators
import json

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
        return ""
    elif not hasattr(content, '__iter__'):
        return ""
    elif isinstance(content, dict):
        for item in content.items():
            document = {item[0]: item[1]}
            output.append(document)
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
        # print(paths)
        for x in output:
            if isinstance(x[list(x.keys())[0]], dict):
                existFlag = True
                temp = x[list(x.keys())[0]]
                for p in paths:
                    if not isinstance(temp, dict):
                        existFlag = False
                        # print("break")
                        break
                    if p in list(temp.keys()):
                        temp = temp[p]
                        print(temp)
                    else:
                        existFlag = False
                        # print("break")
                        break
                if isinstance(temp, dict):
                    existFlag = False
                # print(existFlag)
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
                temp = item[key]
                item = temp
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

    if parsed_url[1] is not None and parsed_url[2] is not None and parsed_url[1] != "" and parsed_url[2] != "":
        mydb = client[parsed_url[1]]
        mycollection = mydb[parsed_url[2]]
        reformatData = "'" + data[1:-1] + "'"
        insertedData = json.loads(reformatData)
        mycollection.replace_one({}, insertedData)
    return 'You successfully updated data in the database'


def process_POST(url, data):
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"
    client = MongoClient(address, int(port))

    if parsed_url[1] is not None and parsed_url[2] is not None and parsed_url[1] != "" and parsed_url[2] != "":
        mydb = client[parsed_url[1]]
        mycollection = mydb[parsed_url[2]]
        reformatData = "'" + data[1:-1] + "'"
        insertedData = json.loads(reformatData)
        mycollection.insert_one(insertedData)
    return 'You successfully inserted to the database'

def process_PATCH(url, data):
    # Parse the data we get from client
    # (curl -X PATCH -d '{"name": "John Smith", "age": 25}' 'https://inf551-1b578.firebaseio.com/users/100.json')
    parsed_url = url.split("/")
    address = "localhost"
    port = 27017

    if len(parsed_url[0].split(":")) == 2:
        address = parsed_url[0].split(":")[0]
        port = parsed_url[0].split(":")[1]
    else:
        return "Invalid Command: invalid address and port"

    # Establish a connection to MongoDB using the provided URL
    # (similar to what you did in the process_GET function)
    client = MongoClient(address, int(port))

    # Check if the data you want to update exists in the database
    # You can use the find_one() method to search for a document
    # matching the conditions provided in the URL
    # If the data exists, update the data
    # Use the update_one() method with the conditions and payload as arguments
    if parsed_url[1] is not None and parsed_url[2] is not None and parsed_url[3] is not None \
            and parsed_url[1] != "" and parsed_url[2] != "" and parsed_url[2] != "":
        db = client[parsed_url[1]]
        collection = db[parsed_url[2]]
        primary_key = parsed_url[3]
        # Find a document with the primary_key field present
        document = collection.find_one({primary_key: {'$exists': True}})

        # Update the document with the provided data
        if document:
            update_data = {"'" + data[1:-1] + "'"}
            result = collection.update_one({primary_key: {'$exists': True}}, {'$set': update_data})
    # If the data does not exist, insert the new data
    # Use the insert_one() method with the payload as the argument
        else:
            insert_one_data = "'" + data[1:-1] + "'"
            inserted_data = json.loads(insert_one_data)
            collection.insert_one(inserted_data)
    # Return a message indicating whether the data was inserted or updated
    return "Success! the PATCH command worked"

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
                process_POST(db_url[7:-5], parsed_command[4])
            elif parsed_command[4] == '-d':
                return process_POST(db_url[7:-5], parsed_command[5])
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
