from pymongo import MongoClient
import validators
import json

command_list = ["GET", "PUT", "POST", "PATCH", "DELETE"]
filter_conds_list = ["orderBy", "limitToFirst", "limitToLast", "equalTo", "startAt", "endAt"]

## TODO: get document from db
## Currently can do get command without filter
def process_GET(url, conditions):
    try: 
        # curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='price'&limitToFirst=5"
        # Process filter conditions for GET command
        orderByIndex = None
        orderByFlag = False
        startValue = None
        endValue = None
        equalValue = None
        sortOrder = 0
        limitToNumber = None
        current_cond_key = []
        find_query = dict()
        if conditions is not None:
            for cond in conditions.split("&"):
                #check if the filter format is valid
                if len(cond.split("="))<2:
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
                if (filter_value[0]=="\'" and filter_value[-1]=="\'") or (filter_value[0]=="\"" and filter_value[-1]=="\""):
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
                    orderByFlag = True
                    orderByIndex = filter_value
                elif filter_key == "limitToFirst":
                    if orderByFlag is not True:
                        return "Invalid Command: please enter orderBy condition first"
                    elif sortOrder < 0 :
                        return "Invalid Command: cannot enter limitToFirst and limitToLast together"
                    elif type(filter_value):
                        return "Invalid Command: limitToFirst only accepts integer"
                    else:
                        sortOrder = 1
                        limitToNumber = filter_value
                elif filter_key == "limitToFirst":
                    if orderByFlag is not True:
                        return "Invalid Command: please enter orderBy condition first"
                    elif sortOrder > 0 :
                        return "Invalid Command: cannot enter limitToFirst and limitToLast together"
                    elif type(filter_value):
                        return "Invalid Command: limitToLast only accepts integer"
                    else:
                        sortOrder = -1
                        limitToNumber = filter_value
                elif filter_key == "startAt":
                    startValue = filter_value
                elif filter_key == "endAt":
                    endValue = filter_value
                elif filter_key == "equalTo":
                    equalValue == filter_value
                else:
                    return "Invalid Command: invalid filter condition"
                    

                print(filter_value)
                print(type(filter_value))
        
        ## Get address and port to establish connection to mongodb
        parsed_url = url.split("/")
        address = "localhost"
        port = 27017

        if len(parsed_url[0].split(":"))==2:
            address = parsed_url[0].split(":")[0]
            port = parsed_url[0].split(":")[1]
        else:
            return "Invalid Command: invalid address and port"
        client = MongoClient(address, int(port))
        if len(parsed_url) == 1:
            # only enter localhost or IP address end with .json -- invalid url form
            ## untested code -- currently unreachable
            output = dict()
            for db_name in client.list_database_names():
                db_content = dict()
                print(db_name)
                db = client[db_name]
                for col_name in db.list_collection_names():
                    col_content = dict()
                    print(col_name)
                    for document in db[col_name].find({},{"_id":0}):
                        col_content.update(document)
                        print(document)
                    db_content.update({col_name:col_content})
                output.update({db_name:db_content})
            return str(output)

        elif len(parsed_url) == 2:
            # Input the IP address and empty database name, return entire MongoDB
            # curl -X GET "http://localhost:27017/.json"
            if parsed_url[1] == "":
                output = dict()
                for db_name in client.list_database_names():
                    db_content = dict()
                    db = client[db_name]
                    for col_name in db.list_collection_names():
                        col_content = []
                        
                        for document in db[col_name].find({},{"_id":0}):
                            col_content.append(document)
                            # print(document)
                        db_content.update({col_name:col_content})
                    output.update({db_name:db_content})
                return str(output)
            # input the IP address and database name, return entire database
            # curl -X GET "http://localhost:27017/DSCI551.json"
            else:
                db_content = dict()
                db = client[parsed_url[1]]
                for col_name in db.list_collection_names():
                    col_content = []
                    for document in db[col_name].find({},{"_id":0}):
                        col_content.append(document)
                        # print(document)
                    db_content.update({col_name:col_content})
                output = dict({parsed_url[1]:db_content})
        # input IP address, database name, and collection name, return entire collection
        elif len(parsed_url) == 3:
            db = client[parsed_url[1]]
            content = []
            for document in db[parsed_url[2]].find({},{"_id":0}):
                content.append(document)
            return content
        else:
            json_keys = parsed_url[3:]
            db = client[parsed_url[1]]
            content = None
            documents = dict()
            for document in db[parsed_url[2]].find({},{"_id":0}):
                documents.update(document)
            item = documents
            for key in json_keys:
                ##print(key)
                if type(item) == dict:
                    temp = item[key]
                    item = temp
                else:
                    item = None
                    break
            if item is not None:
                content = item
            return content
        return str(output)
    except Exception as e:
        print("error occurs")
        return "Invalid Command: " + str(e)


# High-level function for command processing
def command_process(command):
    # parse command by spaces
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
    if not ((parsed_command[3][0]=="\'" and parsed_command[3][-1]=="\'") or (parsed_command[3][0]=="\"" and parsed_command[3][-1]=="\"")):
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
        # TODO: handle post command
        return parsed_command
    elif parsed_command[2].upper() == "PUT":
        # TODO: handle post command
        return parsed_command
    elif parsed_command[2].upper() == "PATCH":
        # TODO: handle post command
        return parsed_command
    elif parsed_command[2].upper() == "DELETE":
        # TODO: handle post command
        return parsed_command
    return parsed_command