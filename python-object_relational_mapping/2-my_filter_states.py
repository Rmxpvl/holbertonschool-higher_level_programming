#!/usr/bin/python3
"""Lists states matching a given name."""

import MySQLdb
from sys import argv

if __name__ == "__main__":

    db = MySQLdb.connect(
        host="localhost",
        port=3306,
        user=argv[1],
        passwd=argv[2],
        db=argv[3]
    )

    cursor = db.cursor()

    query = (
        "SELECT * FROM states WHERE name = '{}' "
        "ORDER BY states.id ASC"
    ).format(argv[4])

    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)

    cursor.close()
    db.close()
