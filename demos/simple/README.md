Demonstration of a simple Python web server with Duo authentication.

Tested with Python 2.7 and Python 3.5.

# Preparation

Review the Duo WebSDK documentation at https://duo.com/docs/duoweb.

# Configuration

To set up, edit duo.conf with the appropriate `ikey`, `skey`, `akey`, and
`host` values.

# Installation

Set up a virtualenv and install the dependencies.

```
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```
# Run the example

To run the server on port 8080:

    python server.py

# Usage

Visit the root URL with a 'user' argument, e.g.
'http://localhost:8080/?user=myname'.

# Multiple Configurations
If desired, multiple configuration sections can be added to `duo.conf`:

```
[duo]
ikey = ikey
skey = skey
akey = akey
host = host

[duo_1]
ikey = ikey
skey = skey
akey = akey
host = host
```

An optional parameter can be passed at runtime. If not provided, it will default to `duo`

    python server.py [-c|--config <config_section>]


