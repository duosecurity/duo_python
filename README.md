# Overview

[![Build Status](https://travis-ci.org/duosecurity/duo_python.svg?branch=master)](https://travis-ci.org/duosecurity/duo_python)

**duo_python** - Duo two-factor authentication for Python web applications: https://duo.com/docs/duoweb

This package allows a web developer to quickly add Duo's interactive, self-service, two-factor authentication to any web login form - without setting up secondary user accounts, directory synchronization, servers, or hardware.

Files located in the `js` directory should be hosted by your webserver for inclusion in web pages.

# Installation

Using `pip`:

`pip install duo_web`.

# Examples
Included are examples for integrating `duo_web` into Google App Engine, Django, and the standard library `HTTPSimpleServer`. See each demo directory for instructions on setup and running.

Development:

```
$ git clone https://github.com/duosecurity/duo_python.git
$ cd duo_python
$ pip install --requirement requirements-dev.txt
```

# Testing

```
$ nose2
```

# Linting

```
$ flake8 --ignore=E501 duo_web/ tests/
```

# Support

Report any bugs, feature requests, etc. to us directly: support@duosecurity.com

