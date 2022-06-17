# Deprecation Notice

Duo Security will deprecate and archive this repository on July 18, 2022. The repository will remain public and visible after that date, and integrations built using this repository’s code will continue to work. You can also continue to fork, clone, or pull from this repository after it is deprecated.

However, Duo will not provide any further releases or enhancements after the deprecation date.

Duo recommends migrating your application to the Duo Universal Prompt. Refer to [our documentation](https://duo.com/docs/universal-prompt-update-guide) for more information on how to update.

For frequently asked questions about the impact of this deprecation, please see the [Repository Deprecation FAQ](https://duosecurity.github.io/faq.html)

----

# Overview

[![Build Status](https://github.com/duosecurity/duo_python/workflows/Python%20CI/badge.svg?branch=master)](https://github.com/duosecurity/duo_python/actions)
[![Issues](https://img.shields.io/github/issues/duosecurity/duo_python)](https://github.com/duosecurity/duo_python/issues)
[![Forks](https://img.shields.io/github/forks/duosecurity/duo_python)](https://github.com/duosecurity/duo_python/network/members)
[![Stars](https://img.shields.io/github/stars/duosecurity/duo_python)](https://github.com/duosecurity/duo_python/stargazers)
[![License](https://img.shields.io/badge/License-View%20License-orange)](https://github.com/duosecurity/duo_python/blob/master/LICENSE)

**duo_python** - Duo two-factor authentication for Python web applications: https://duo.com/docs/duoweb-v2

Duo has released a new Python client that will let you integrate the Duo Universal Prompt into your web applications.
Check out https://duo.com/docs/duoweb for more info on the Universal Prompt and [duo_universal_python](https://github.com/duosecurity/duo_universal_python) for the new client.

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

