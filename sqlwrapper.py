#!/usr/bin/env python

# Copyright (c) 2016 Aaron Zhao
# Copyright (c) 2016 Gabriel Esposito
# See LICENSE for details.

"""
Flexible Python wrapper for a local MySQL server to be served over an API.
"""

import pymysql

# Turn pymysql warnings into errors
import warnings
warnings.filterwarnings('error')


class RESTWrapper:
    """Implement a SQL wrapper with REST philosophy. One query/connection."""

    def __init__(self, host, username, password, database):
        self.connection = pymysql.connect(host=host,
                                          user=username,
                                          password=password,
                                          db=database,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def _execute_query(self, query):
        """Run query with pymysql and handle connections and commits."""

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
        finally:
            self.connection.commit()
            self.connection.close()
        return cursor

    def query(self, action, table, **kwargs):
        """
        Run a mysql query on a table.
        Sanitizes inputs with scrub().
        **kwargs is field, value
        """

        if action == 'insert':
            ins = "INSERT INTO `" + scrub(table) + "` "

            fields = '(' + ', '.join(["`" + scrub(name) + "`" for name, value in kwargs.items()]) + ')'
            values = '(' + ', '.join(["'" + scrub(value) + "'" for name, value in kwargs.items()]) + ')'

            query = ins + fields + " VALUES " + values

            cursor = self._execute_query(query)
            
            return cursor.lastrowid
        elif action in ['delete', 'select']:
            if action == 'delete':
                head = "DELETE FROM `" + scrub(table) + "` "
            else:
                head = "SELECT * FROM `" + scrub(table) + "` "

            comparators = ' AND '.join(["`" + scrub(name) + "`='" + scrub(value) + "'" for name, value in kwargs.items()])

            if comparators:
                query = head + " WHERE " + comparators
            else:
                query = head.rstrip()

            cursor = self._execute_query(query)

            if action == 'delete':
                return True
            return cursor.fetchall()

    def query_passthru(self, query):
        """Run the query directly using pymysql. Does NOT sanitize."""
        
        cursor = self._execute_query(query)
        return cursor.fetchall()


def scrub(string, exclude=[]):
    """
    Avoid SQL injection attacks.
    Only return alphanumeric characters or
    the contents of exclude that are in the original string.
    """
    
    return ''.join([char for char in string if char.isalnum() or char in exclude])
