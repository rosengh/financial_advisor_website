import json
import os
#empty_data should be what data we want to put on there of the file doesnt exist
# either {} or [] as we are working with json files
def create_if_not_exist(filename, empty_data):
    if not os.path.exists(filename): #if the file not exist then i have create a json file with empty data in it
        write_json_file(filename, empty_data)

def write_json_file(filename, info_to_save):
    with open(filename, "w") as file:
        json.dump(info_to_save, file, indent=4)

def read_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    print("Read Success!")
    return data

