import base64
import os
from time import sleep
from typing import Optional

from flask import Flask, abort, jsonify, request
import requests

from registration_ref.crypto import sign_device_csr
from registration_ref.sota_toml import sota_toml_fmt
from registration_ref.settings import Settings

app = Flask(__name__)


@app.before_request
def _auth_user():
    pass


def log_device(uuid: str, client_key: str, name: str):
    # Keep a log of created devices
    with open(os.path.join(Settings.DEVICES_DIR, uuid), "w") as f:
        # save data as json for ease of parsing later
        # for debugging only
        # print(client_key)

        base64_client_key_bytes = client_key.encode("ascii")
        base64_encoded_client_key_bytes = base64.b64encode(base64_client_key_bytes)
        base64_encoded_client_key_string = base64_encoded_client_key_bytes.decode("ascii")

        device_detail = jsonify (
            {
                "uuid": uuid,
                "name": name,
                "client_key": base64_encoded_client_key_string
            }
        ).get_data(as_text=True)

        f.write(device_detail)

        # for debugging only
        # print(base64.b64decode(base64_encoded_client_key_string.encode("ascii")).decode("ascii"))


def create_in_foundries(client_cert: str, api_token: str, name: Optional[str] = None):
    data = {
        "client.pem": client_cert,
    }
    if Settings.DEVICE_GROUP:
        data["group"] = Settings.DEVICE_GROUP
    if name:
        data["name"] = name

    headers: dict = {
        "OSF-TOKEN": api_token,
    }
    for x in (0.1, 0.2, 1, 0):
        r = requests.put(
            "https://api.foundries.io/ota/devices/", headers=headers, json=data
        )
        if r.status_code == 409:
            abort(409, description=r.text)
        if r.ok:
            return
        msg = f"Unable to create device on server: HTTP_{r.status_code} - {r.text}"
        app.logger.error(msg)
        if x:
            app.logger.info("Trying again in %ds", x)
            sleep(x)
        else:
            abort(500, description=msg)


@app.route("/sign", methods=["POST"])
def sign_csr():
    data = request.get_json()
    if not data:
        abort(400, description="Missing request body")

    csr = data.get("csr")
    if not csr:
        abort(400, description="Missing required field 'csr'")
    if not isinstance(csr, str):
        abort(400, description="Invalid data type for 'csr'")

    hwid = data.get("hardware-id")
    if not hwid:
        abort(400, description="Missing required field 'hardware-id'")

    overrides = data.get("overrides") or {}
    sota_config_dir = data.get("sota-config-dir") or "/var/sota"
    name = data.get("name") or None

    if data.get("group"):
        # Since we run w/o any authentication, allowing devices to determine
        # their device group is too dangerous to allow by default. We instead
        # allow a server defined config, Settings.DEVICE_GROUP.
        abort(400, description="Registration-reference does not support 'group' field")

    try:
        fields = sign_device_csr(csr)
    except ValueError as e:
        abort(400, description=str(e))

    if Settings.API_TOKEN_PATH:
        with open(Settings.API_TOKEN_PATH) as f:
            tok = f.read().strip()
            if tok:
                app.logger.info("Creating in foundries with %s", fields.uuid)
                create_in_foundries(fields.client_crt, tok, name)

    log_device(fields.uuid, fields.client_crt, name)

    return (
        jsonify(
            {
                "root.crt": fields.root_crt,
                "sota.toml": sota_toml_fmt(hwid, overrides, sota_config_dir),
                "client.pem": fields.client_crt,
                "client.chained": fields.client_crt + "\n" + Settings.CA_CRT,
            },
        ),
        201,
    )
