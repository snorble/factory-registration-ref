"""
Script to process all the registered devices on the production line and
adds them to the factory with the correct name
"""

# Standard Library Imports
import base64
import json
import os
import requests


DEVICES_PATH = "/home/thomas/git/factory-registration-ref/data/devices"
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
        data = {"client.pem": client_key, "name": device_data["name"]}

        response = requests.put(ENDPOINT, headers=headers, json=data)

        if response.status_code == 409:
            print("device already added:", device_data["uuid"])
            # remove device
            print("removing device file: ", device_data["uuid"])
            # os.remove(device_path)

        elif response.status_code == 201:
            print("device successfully added:", device_data["uuid"])
            # check device before removing

            device_get_response = requests.get(ENDPOINT + "/" + device_data["name"], headers=headers)
            if device_get_response.status_code == 200:
                # check UUID matches before removing
                factory_device_data = device_get_response.json()
                if factory_device_data["uuid"] == device_data["uuid"]:
                    print("removing device file: ", device_data["uuid"])
                    # remove device
                    os.remove(device_path)
        else:
            # otherwise some error occurred
            print(response.status_code, " : ", response.text)
