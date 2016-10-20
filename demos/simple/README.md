Demonstration of a simple Python web server with Duo authentication.

Tested with Python 2.7 and Python 3.5.

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



