#Introduction

## Flaskr + DUO = 2FA your login

## How to use
Assuming you already have Flaskr setup just run ``` python flaskr.py ``` in the main directory of this repository.
Open a browser session to the URL specified by Flask. By default it is ```http://127.0.0.1:5000/```

Please see the section on **Configuration Files** to setup your authentication keys. The

##About
This is being used as a proof of concept for setting up 2FA on a basic web login using Python.

##Configuration files:

This application relies on two configuration files that follow the standard .ini format.

###app.conf:
```
; My App configuration

[app]
skey = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
The skey above should is used to sign the session cookie for login. It can be any alphanumeric string of 40 or greater.
This will be read through ConfigParser() into a dictionary. The values can be accessed as

    config.get('app','skey')

Which will return the value stored next to the `skey` value that is used to sign the login cookies.

###duo.conf
```
; Duo integration config

[duo]

ikey = <your ikey>
skey = <your skey>
akey = <your generated akey>
host = <your api-hostname>
```
