from pymongo import MongoClient
import validators
import json

command_list = ["GET", "PUT", "POST", "PATCH", "DELETE"]
filter_conds_list = ["orderBy", "limitToFirst", "limitToLast", "equalTo", "startAt", "endAt"]


## helper function -- input a dict and a path/list of keys, return the value corresponding to the path/list of keys in the list
def dict_keys_helper(dict_, keys):
    if not isinstance(dict_, dict):
        return dict_
    output = dict_
    for key in keys:
        if key in list(output.keys()):
            temp = output[key]
            output = temp
    return output

    


## helper function -- help GET command to product appropriate output of filter condition
def filter_process(content, condition_query):
    orderBy = condition_query["orderBy"]  
    limitValue = condition_query["limitValue"]
    startAt = condition_query["startAt"]
    endAt = condition_query["endAt"]
    equalTo = condition_query["equalTo"]
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
        output = sorted(output, key = lambda x: list(x.keys())[0])
        #curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='$Key'&equalTo='0987654321'"
        if equalTo is not None:
            temp = [document for document in output if list(document.keys())[0] == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if list(document.keys())[0] >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if list(document.keys())[0] <= endAt]
            output = temp
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    #process orderby $value
    #curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='$value'
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
            temp = [document for document in output if document[list(document.keys())[0]] == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if document[list(document.keys())[0]] >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if document[list(document.keys())[0]] <= endAt]
            output = temp
        output += non_sort
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]
    #handle filter orderby a specific key or path of keys
    #curl -X GET "http://localhost:27017/DSCI551/books.json?orderBy='price'&endAt=30&limitToLast=3"
    else:
        can_sort = []
        non_sort = []
        paths = orderBy.split("/")
        #print(paths)
        for x in output:
            if isinstance(x[list(x.keys())[0]], dict):
                existFlag = True
                temp = x[list(x.keys())[0]]
                for p in paths:
                    if not isinstance(temp, dict):
                        existFlag = False
                        #print("break")
                        break
                    if p in list(temp.keys()):
                        temp = temp[p]
                        print(temp)
                    else:
                        existFlag = False
                        #print("break")
                        break
                if isinstance(temp, dict):
                    existFlag = False
                #print(existFlag)
                if existFlag:
                    can_sort.append(x)
                else:
                    non_sort.append(x)
            else:
                non_sort.append(x)
        can_sort = sorted(can_sort, key=lambda x: dict_keys_helper(x[list(x.keys())[0]], paths))
        print(can_sort)
        output = can_sort
        if equalTo is not None:
            temp = [document for document in output if dict_keys_helper(document[list(document.keys())[0]], paths) == equalTo]
            output = temp
        if startAt is not None:
            temp = [document for document in output if dict_keys_helper(document[list(document.keys())[0]], paths) >= startAt]
            output = temp
        if endAt is not None:
            temp = [document for document in output if dict_keys_helper(document[list(document.keys())[0]], paths) <= endAt]
            output = temp
        output += non_sort
        if limitValue is not None:
            if abs(limitValue) >= len(output):
                pass
            elif limitValue > 0:
                output = output[:limitValue]
            elif limitValue < 0:
                output = output[limitValue:]

    return output

## TODO: get document from db
## Currently can do get command without filter
def process_GET(url, conditions):
    try: 
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
                    orderByIndex = filter_value
                    condition_query.update({"orderBy": orderByIndex})
                elif filter_key == "limitToFirst":
                    if limitOrder < 0 :
                        return "Invalid Command: cannot enter limitToFirst and limitToLast together"
                    elif not isinstance(filter_value, int):
                        return "Invalid Command: limitToFirst only accepts integer"
                    else:
                        limitOrder = 1
                        limitToNumber = filter_value
                        condition_query.update({"limitValue": limitOrder * limitToNumber})
                elif filter_key == "limitToLast":
                    if limitOrder > 0 :
                        return "Invalid Command: cannot enter limitToFirst and limitToFirst together"
                    elif not isinstance(filter_value, int):
                        return "Invalid Command: limitToLast only accepts integer"
                    else:
                        limitOrder = -1
                        limitToNumber = filter_value
                        condition_query.update({"limitValue": limitOrder * limitToNumber})
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
        # curl -X GET "http://localhost:27017/DSCI551/books.json"
        elif len(parsed_url) == 3:
            db = client[parsed_url[1]]
            content = []
            for document in db[parsed_url[2]].find({},{"_id":0}):
                content.append(document)
            return filter_process(content, condition_query)
        # curl -X GET "http://localhost:27017/DSCI551/books/1234567890.json"
        # curl -X GET "http://localhost:27017/DSCI551/books/1234567890/price.json"
        else:
            json_keys = parsed_url[3:]
            db = client[parsed_url[1]]
            content = None
            documents = []
            for document in db[parsed_url[2]].find({},{"_id":0}):
                documents.append(document)
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