from pymongo import MongoClient
import validators
import json

command_list = ["GET"]
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
            output = dict((db, [collection for collection in client[db].collection_names()]) for db in client.database_names())
            return output
        elif len(parsed_url) == 2:
            ## TODO
            if parsed_url[1] == "":
                output = dict()
                for db_name in client.database_names():
                    db = client[db_name]
                    for col_name in db.list_collection_names():
                        for document in db[col_name]:
                            print(document)
                return output
            else:
                db = client[parsed_url[1]]
        return str(parsed_url)
    except:
        print("error occurs")
        return "Invalid Commnad: error occurs"

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