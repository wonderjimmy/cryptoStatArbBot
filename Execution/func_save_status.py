import json

# save status
def save_status(dict):
    with open("status.json", "w") as fp:
        json.dump(dict, fp, indent=4)