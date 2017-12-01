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

## CRITICAL: Add Duo to logins for `/admin` as well

The examples herein do not add Duo "everywhere" nor the Django admin site. **This is critical to recognize, because if you do not have 2FA on `/admin`, and you have `/admin` enabled, you essentially degrade to 1FA on the most sensitive part of your application.**

Happily it is not difficult! You just have some choices to make about how to do it. 

You can choose to add Duo "everywhere" (except login and logout) by applying middleware; [here is some discussion and examples of this approach](https://stackoverflow.com/questions/2164069/best-way-to-make-djangos-login-required-the-default). There is a [third party library, `django-stronghold`, which can achieve the same effect](https://github.com/mgrouchy/django-stronghold); however, you can avoid adding a dependency by just inlining your own middleware (it does not take much code).

If you do not want to add it "everywhere" you can just make sure to add it to the admin site explicitly. Due to the typical "shortcut" fashion that admin views are added to your configuration, you have some choices to make in how you add the `duo_auth_required` decorator to all admin views. You basically want some helper to go through all child views and decorate them. [There are multiple approaches discussed here, including at least one third party library](https://stackoverflow.com/q/2307926/884640).

Whichever way you choose to do it, don't leave the admin panel less secure!

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

