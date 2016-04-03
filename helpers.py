#!/usr/bin/env python

# Copyright (c) 2016 Aaron Zhao
# Copyright (c) 2016 Gabriel Esposito
# See LICENSE for details.

"""
Helper functions for the server.
"""

import decimal
from math import acos, cos, sin
import ConfigParser

EARTH_R = 3959  # Miles


def point_near(lat, lng, rlat, rlng, r):
    """Returns true if the point for lat, lng is within r miles of rlat, rlng"""

    # Shortest distance between two given points
    return acos(sin(lat) * sin(rlat) + cos(lat) * cos(rlat) * cos(lng - rlng)) * EARTH_R < r

def dec_default(obj):
    """Default function for json.dumps() to allow serialization of Decimal() from pymysql."""
    
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def create_config():
    """
    Creates the config for the server.
    Example config:
    
    [mysql]
    user=textbooks
    pass=textbooks
    host=localhost
    db=textbooks

    [oAuth]
    server_client_id=validtoken
    android_client_id=validtoken
    
    [http]
    host=localhost
    port=8080
    
    """
    
    def check_number(prompt):
        while True:
            try:
                input = int(raw_input(prompt))
                return input
            except ValueError:
                print "Must be a number."

    
    print "Config not present. Creating config."
    
    config = ConfigParser.RawConfigParser()
    config.add_section('http')
    config.set('http', 'host', str(raw_input("Hostname: ")))
    config.set('http', 'port', str(check_number("Port: ")))
    config.add_section('oAuth')
    config.set('oAuth', 'server_client_id', str(raw_input("oAuth Server Client ID: ")))
    config.set('oAuth', 'android_client_id', str(raw_input("oAuth Android Client ID: ")))
    config.add_section('mysql')
    config.set('mysql', 'user', str(raw_input("MySQL User: ")))
    config.set('mysql', 'pass', str(raw_input("MySQL Password: ")))
    config.set('mysql', 'host', str(raw_input("MySQL Host: ")))
    config.set('mysql', 'db', str(raw_input("MySQL Database: ")))
    
    with open('server.cfg', 'wb') as configfile:
        config.write(configfile)    

    print "Config created."
