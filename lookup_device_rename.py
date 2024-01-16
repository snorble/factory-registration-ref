"""
Script to process all the registered devices on the production line and
adds them to the factory with the correct name
"""

# Standard Library Imports
import base64
import json
import os
import requests


DEVICES_PATH = "/home/thomas/Downloads/factory-registrations-12-30/update_name"
TOKEN_PATH = "/home/thomas/git/factory-registration-ref/token/create_device_scope"

ENDPOINT = "https://api.foundries.io/ota/devices/"

with open(os.path.join(TOKEN_PATH), "r") as f:
    api_token = f.read().replace("\n", "")

for device in os.listdir(DEVICES_PATH):
    device_path = os.path.join(DEVICES_PATH, device)
    with open(device_path) as f:
        device_data = json.load(f)

        # decode client key
        client_key_bytes = device_data["client_key"].encode("ascii")
        client_key = base64.b64decode(client_key_bytes).decode("ascii")

        # add device
        headers = {"OSF-TOKEN": api_token}
        
        response = requests.get(ENDPOINT + "/" + device_data["uuid"], headers=headers)

        if response.status_code == 404:
            print("device not found:", device_data["uuid"])
        elif response.status_code == 200:
            print("device found:", device_data["uuid"])
            print("device details", response)
            # rename device
            update_data = {"name": device_data["name"]}
            device_get_response = requests.patch(ENDPOINT + "/" + device_data["uuid"], headers=headers, json=update_data)
            if device_get_response.status_code == 200:
                print("device renamed from: ", device_data["uuid"], "to: ", device_data["name"])
        else:
            # otherwise some error occurred
            print(response.status_code, " : ", response.text)

