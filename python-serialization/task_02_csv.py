#!/usr/bin/env python3

import csv
import json

def convert_csv_to_json(CSV_filename):
    data = []
    with open(CSV_filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
