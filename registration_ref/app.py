from flask import Flask, abort, jsonify, request

from registration_ref.crypto import sign_device_csr
from registration_ref.sota_toml import sota_toml_fmt

app = Flask(__name__)


@app.before_request
def _auth_user():
    pass


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

    overrides = data.get("overrides") or {}
    sota_config_dir = data.get("sota-config-dir") or "/var/sota"

    try:
        fields = sign_device_csr(csr)
    except ValueError as e:
        abort(400, description=str(e))

    return (
        jsonify(
            {
                "root.crt": fields.root_crt,
                "sota.toml": sota_toml_fmt(overrides, sota_config_dir),
                "client.pem": fields.client_crt,
            },
        ),
        201,
    )
