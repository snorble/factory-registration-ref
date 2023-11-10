Foundries.io allows customers to own/manage their own PKI for their factory's
device-gateway. This project provides a reference example of an
lmp-device-register compatible API that can be used with a customer owned
intermediate certificate authority.

This code can be used as-is or forked to accomodate the specific customer
manufacturing needs.

# Requirements:
 * docker-compose
 * git
 * access to your PKI files created/managed via fioctl

# Quick Start

First create/register your PKI with Foundries.io:
~~~
  $ fioctl keys ca create /really-secure-directory
~~~

Next set this project up with:
~~~
 $ git clone git@github.com:snorble/factory-registration-ref.git
 $ cd factory-registration-ref
 $ docker-compose build
~~~

Now copy the required files to this service:
~~~
 $ mkdir -p ./data/certs
 $ cp /really-secure-directory/factory_ca.pem ./data/certs/
 $ cp /really-secure-directory/local-ca.pem ./data/certs/
 $ cp /really-secure-directory/local-ca.key ./data/certs/
 $ cp /really-secure-directory/tls-crt ./data/certs/

 # some of these files are only readable to the file owner. To deal with
 # docker user permissions the easy way:
 chmod +r ./data/certs/*
~~~
 
 A Foundries.io API token (scope `devices:create` and `devices:read`) can be obtained and saved as ./token/create_device_scope
 This is used by the add_devices_async.py to properly name the newly added device in foundries
~~~
$ mkdir ./token
~~~

You can optionally copy a Foundries.io API token (scope `devices:create`) so
that devices can be defined/configured before the certificate is returned back
to the device. This can be used for setting up device-groups and config so
that a device's first boot will include the proper configuration:
~~~
  # echo <TOKEN> > ./data/fio-api-token
~~~

You can now run this API with:
~~~
 $ docker-compose up
~~~

To register a device, run as root from LmP device:
~~~
 $ DEVICE_API=http://<IP of docker-compose host>/sign lmp-device-register [-T <TOKEN>] [-f <factory>]
~~~

Example, Host Machine IP address of 192.168.0.11, with PRODUCTION flag on, and name of device as i350-snorble-442d67aaaa05
~~~
DEVICE_API=http://192.168.0.36/sign PRODUCTION=on lmp-device-register -t factory -T na -n i350-snorble-442d67aaaa05
~~~

**NOTE** If you're emulating the device with QEMU, by default the gateway (host) IP is `10.0.2.2`.
(i.e. `sudo DEVICE_API=http://10.0.2.2:80/sign lmp-device-register [-T <TOKEN>] [-f <factory>]`)

# Pre-Adding Device to Foundries
This is used to rename the Device using UUID as a name to having Serial Number as the name.  It looks at the ./data/devices folder and processes each newly added device by pre-adding them to foundries with the correct name.  The first time the Doll is onboarded and brought online, it will attach to the correctly named pre-added Device in foundries.  

This script is run at the end of the day as a last step to pre-add all the Dolls that have been registered with the above Registration Process  

Ensure this script is run with sudo privileges: `sudo python3 add_devices_async.py`  
Once a Device is successfully pre-added to foundries, the file in ./data/devices folder is removed

# Testing/Troubleshooting
This project includes a simple `fake-lmp-device-register` that can be used
to quickly test this project's API.
