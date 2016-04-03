# Textbook-Server
Server for location-based university textbook marketplace app (https://github.com/Aaron-Zhao/Textbookbns)

# Dependencies & setup
```
sudo apt-get install build-essential python-dev python-pip python-virtualenv libffi-dev libssl-dev
(optional) virtualenv env
(sudo) pip install webapp2 webob pymysql oauth2client paste
```

# Usage
Run server.py and it will fill out the config for you and launch. An example config is in helpers.py.
```
(optional) source env/bin/activate
python server.py
```
