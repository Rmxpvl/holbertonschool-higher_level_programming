#!/usr/bin/python3
"""Flask application displaying product data from JSON, CSV, or SQLite."""
import csv
import json
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)


def read_json(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def read_csv(filename):
    products = []
    with open(filename, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            products.append({
                'id': int(row['id']),
                'name': row['name'],
                'category': row['category'],
                'price': float(row['price']),
            })
    return products


def read_sql(product_id=None):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    if product_id is not None:
        cursor.execute(
            'SELECT id, name, category, price FROM Products WHERE id = ?',
            (product_id,)
        )
    else:
        cursor.execute('SELECT id, name, category, price FROM Products')
    rows = cursor.fetchall()
    conn.close()
    return [
        {'id': row[0], 'name': row[1], 'category': row[2], 'price': row[3]}
        for row in rows
    ]


@app.route('/products')
def products():
    source = request.args.get('source')
    product_id = request.args.get('id')

    if product_id is not None:
        try:
            product_id = int(product_id)
        except ValueError:
            return render_template('product_display.html',
                                    error="Product not found")

    if source == 'json':
        data = read_json('products.json')
        if product_id is not None:
            data = [product for product in data if product['id'] == product_id]
    elif source == 'csv':
        data = read_csv('products.csv')
        if product_id is not None:
            data = [product for product in data if product['id'] == product_id]
    elif source == 'sql':
        try:
            data = read_sql(product_id)
        except sqlite3.Error:
            return render_template('product_display.html',
                                    error="Error fetching data from database")
    else:
        return render_template('product_display.html', error="Wrong source")

    if product_id is not None and not data:
        return render_template('product_display.html',
                                error="Product not found")

    return render_template('product_display.html', products=data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
