#!/usr/bin/env python

# Copyright (c) 2016 Aaron Zhao
# Copyright (c) 2016 Gabriel Esposito
# See LICENSE for details.

"""
REST API for Android Textbook Marketplace App.
"""

import os
import json
import decimal
import ConfigParser
import traceback

import webapp2
from oauth2client import crypt, client

from sqlwrapper import RESTWrapper, scrub
from helpers import point_near, dec_default, create_config

config = ConfigParser.ConfigParser()

# Make sure server config exists, if not, set it up
if not os.path.isfile('server.cfg'):
    create_config()
config.read('server.cfg')

SQLuser = config.get('mysql', 'user')
SQLpass = config.get('mysql', 'pass')
SQLHost = config.get('mysql', 'host')
SQLDB = config.get('mysql', 'db')

oAuthServerClientID = config.get('oAuth', 'server_client_id')
oAuthAndroidClientID = config.get('oAuth', 'android_client_id')

ServerHost = config.get('http', 'host')
ServerPort = config.get('http', 'port')


class AppAPI(webapp2.RequestHandler):
    """Request handler API class. Takes care of GET and POST requests."""

    def verify_oauth_token(self, token):
        """Verify the oAuth token with Google"""

        try:
            print "Verifying token"
            token = client.verify_id_token(token, oAuthServerClientID)
            print 'Token: %s' % token

            if token['aud'] != oAuthServerClientID:
                raise crypt.AppIdentityError("Unrecognized server.")
            if token['azp'] != oAuthAndroidClientID:
                raise crypt.AppIdentityError("Unrecognized client.")
            if token['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("Wrong Issuer.")

            return token['email']
        except Exception, e:
            print e
            print traceback.format_exc()

        return None

    def verify_permissions(self, req, email):
        """Essentially allow everyone to read, but only the creator of a record can write/delete"""

        if req['action'] in ['delete', 'update']:
            if 'SellerID' in req.keys():
                if req['SellerID'] == email:
                    return True
            elif 'Receiver' in req.keys():
                if req['Receiver'] == email:
                    return True
            elif 'UserID' in req.keys():
                if req['UserID'] == email:
                    return True
            raise Exception('SellerID does not match the account used to insert this row')
            return False
        else:
            return True

    def get(self):
        """Handle GET requests by passing to SQL wrapper. Respond with JSON."""

        self.response.headers['Content-Type'] = 'application/json'
        print self.request.GET
        try:
            email = self.verify_oauth_token(self.request.GET['token'])
            if email and self.verify_permissions(self.request.GET, email):
                action = self.request.GET['action']
                if action in ['select', 'delete', 'insert', 'update']:

                    table = self.request.GET['table']

                    wr = RESTWrapper(SQLHost, SQLuser, SQLpass, SQLDB)

                    sql_args = self.request.GET
                    del sql_args['token']
                    del sql_args['action']
                    del sql_args['table']

                    res = wr.query(action, table, **sql_args)

                    if action in ['select', 'insert']:
                        self.response.write(json.dumps({"error": "", "message": res}, default=dec_default))
                    else:
                        self.response.write(json.dumps({"error": "", "message": "Successful"}))
                elif action == 'getsalesnearby':

                    lat = double(scrub(self.request.GET['lat']))
                    lng = double(scrub(self.request.GET['long']))
                    radius = int(scrub(self.request.GET['r']))

                    wr = RESTWrapper(SQLHost, SQLuser, SQLpass, SQLDB)

                    res = wr.query_passthru("""SELECT * FROM Sale WHERE Lat IS NOT NULL AND Lng IS NOT NULL""")

                    nearest = []

                    # Find sales within r miles of user
                    for row in res:
                        if point_near(lat, lng, row['Lat'], row['Lng'], r):
                            nearest.append(row)

                    self.response.write(json.dumps({"error": "", "message": nearest}, default=dec_default))
                else:
                    self.response.write(json.dumps({"error": "Invalid action", "message": ""}))
            else:
                self.response.set_status(401)
                self.response.write(json.dumps({"error": "Unauthorized token or bad permissions (You can only delete and update records you created)", "message": ""}))
        except KeyError, e:
            print e
            print traceback.format_exc()
            self.response.write(json.dumps({"error": "Malformed GET request", "message": ""}))
        except Exception, e:
            print e
            print traceback.format_exc()
            self.response.write(json.dumps({"error": str(e), "message": ""}))

app = webapp2.WSGIApplication([
    ('/api', AppAPI),
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host=ServerHost, port=ServerPort)
    # TODO: HTTPS
    # ssl_pem="cert/self-signed.pem"

if __name__ == '__main__':
    main()
