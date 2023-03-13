from pymongo import MongoClient
import validators
import json

command_list = ["GET"]

## TODO: get document from db
## Currently able to display entire mongodb or a single db
def process_GET(url):
    
    try:
        parsed_url = url.split("/")
        #print(str(parsed_url))
        address = "localhost"
        port = 27017
        if len(parsed_url[0].split(":"))==2:
            address = parsed_url[0].split(":")[0]
            port = parsed_url[0].split(":")[1]
        else:
            return "Invalid Command: invalid address and port"
        client = MongoClient(address, int(port))

        if len(parsed_url) == 1:
            ## untested code -- currently unreachable part
            output = dict()
            for db_name in client.list_database_names():
                db_content = dict()
                print(db_name)
                db = client[db_name]
                for col_name in db.list_collection_names():
                    col_content = dict()
                    print(col_name)
                    for document in db[col_name].find({}):
                        col_content.update(document)
                        print(document)
                    db_content.update({col_name:col_content})
                output.update({db_name:db_content})
            return str(output)
            # output = dict((db, [collection for collection in client[db].collection_names()]) for db in client.database_names())
            # return output
        elif len(parsed_url) == 2:

            if parsed_url[1] == "":
                output = dict()
                for db_name in client.list_database_names():
                    db_content = dict()
                    print(db_name)
                    db = client[db_name]
                    for col_name in db.list_collection_names():
                        col_content = dict()
                        print(col_name)
                        for document in db[col_name].find({}):
                            col_content.update(document)
                            print(document)
                        db_content.update({col_name:col_content})
                    output.update({db_name:db_content})
                return str(output)
            else:
                db_content = dict()
                db = client[parsed_url[1]]
                for col_name in db.list_collection_names():
                    col_content = dict()
                    print(col_name)
                    for document in db[col_name].find({}):
                        col_content.update(document)
                        print(document)
                    db_content.update({col_name:col_content})
                output = dict({parsed_url[1]:db_content})
        return str(output)
    except Exception as e:
        print("error occurs")
        return "Invalid Command: " + str(e)

def command_process(command):
    parsed_command = command.split(" ")
    print(parsed_command)
    if parsed_command[0].lower() != "curl":
        return "Invalid Command: only accept curl command"
    if parsed_command[1].lower() != "-x":
        return "Invalid Command: invalid option, please enter \"-X\" option"
    if parsed_command[2].upper() not in command_list:
        return "Invalid Command: only accept GET, POST, PATCH, DELETE command"
    if not ((parsed_command[3][0]=="\'" and parsed_command[3][-1]=="\'") or (parsed_command[3][0]=="\"" and parsed_command[3][-1]=="\"")):
        return "Invalid Command: please enter url with parenthesis"
    if not validators.url(parsed_command[3][1:-2]):
        return "Invalid Command: " + parsed_command[3] + " is invalid url"
    url = parsed_command[3][1:-1]
    if url[0:7] != "http://" or url[-5:] != ".json":
        print(url[7:-5])
        return "Invalid Command: enter url starts with \'http://\' and ends with \'.json\'"
    if parsed_command[2].upper() == "GET":
        return process_GET(url[7:-5])
    return parsed_command