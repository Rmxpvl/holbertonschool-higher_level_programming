#!/usr/bin/python3
"""Lists all cities of a given state safely."""

import MySQLdb
from sys import argv

if __name__ == "__main__":
    if len(argv) != 5:
        exit(1)

    try:
        db = MySQLdb.connect(
            host="localhost",
            port=3306,
            user=argv[1],
            passwd=argv[2],
            db=argv[3]
        )

        cursor = db.cursor()

        query = """
            SELECT cities.name
            FROM cities
            INNER JOIN states ON cities.state_id = states.id
            WHERE states.name = %s
            ORDER BY cities.id
        """

        cursor.execute(query, (argv[4],))

        cities = [city[0] for city in cursor.fetchall()]
        if cities:
            print(", ".join(cities))

        cursor.close()
        db.close()
    except MySQLdb.Error:
        exit(1)
