#!/bin/sh -e

# if FLASK_DEBUG is defined, we'll run via flask with dynamic reloading of
# code changes to disk. This is helpful for debugging something already in k8s

CERTS_DIR=${CERTS_DIR-/certs}

assert_file() {
	if [ ! -f ${CERTS_DIR}/$1 ] ; then
		echo ERROR: Missing file: ${CERTS_DIR}/$1
		exit 1
	fi
}

assert_file factory_ca.pem
assert_file local-ca.pem
assert_file local-ca.key
export ROOT_CRT=$(cat ${CERTS_DIR}/factory_ca.pem)
export CA_CRT=$(cat ${CERTS_DIR}/local-ca.pem)
export CA_KEY=$(cat ${CERTS_DIR}/local-ca.key)

if [ -z "$FLASK_DEBUG" ] ; then
	exec /usr/bin/gunicorn -n intel-esh -w4 -b 0.0.0.0:8000 $FLASK_APP
fi

exec flask run -h 0.0.0.0 -p 8000
