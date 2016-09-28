# Overview

**duo_python** - Duo two-factor authentication for Python web applications: https://duo.com/docs/duoweb

This package allows a web developer to quickly add Duo's interactive, self-service, two-factor authentication to any web login form - without setting up secondary user accounts, directory synchronization, servers, or hardware.

Files located in the `js` directory should be hosted by your webserver for inclusion in web pages.

# Installing

Development:

```
$ git clone https://github.com/duosecurity/duo_python.git
$ cd duo_python
$ pip install --requirement requirements-dev.txt
```

System:

```
$ pip install duo_web
```

# Using

See the `demos` folder for how to use this library.

# Test

```
$ nose2
```

# Lint

```
$ flake8 --ignore=E501 duo_web/ tests/
```

# Support

Report any bugs, feature requests, etc. to us directly: support@duosecurity.com

