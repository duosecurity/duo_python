# Overview

[![Build Status](https://travis-ci.org/duosecurity/duo_python.svg?branch=master)](https://travis-ci.org/duosecurity/duo_python)
[![Issues](https://img.shields.io/github/issues/duosecurity/duo_python)](https://github.com/duosecurity/duo_python/issues)
[![Forks](https://img.shields.io/github/forks/duosecurity/duo_python)](https://github.com/duosecurity/duo_python/network/members)
[![Stars](https://img.shields.io/github/stars/duosecurity/duo_python)](https://github.com/duosecurity/duo_python/stargazers)
[![License](https://img.shields.io/badge/License-View%20License-orange)](https://github.com/duosecurity/duo_python/blob/master/LICENSE)

**duo_python** - Duo two-factor authentication for Python web applications: https://duo.com/docs/duoweb

Duo has released a new Python client that will let you integrate the Duo Universal Prompt into your web applications.
Check out https://duo.com/docs/duoweb-v4 for more info on the Universal Prompt and [duo_universal_python](https://github.com/duosecurity/duo_universal_python) for the new client.

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
$ flake8
```

# Support

Report any bugs, feature requests, etc. to us directly: support@duosecurity.com

