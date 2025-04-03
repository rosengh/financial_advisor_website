import json

def open_file(filename):
    with open(filename, "r") as file:
        json.load(file)
