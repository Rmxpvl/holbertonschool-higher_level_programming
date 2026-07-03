#!/usr/bin/python3
"""Flask application displaying product data from JSON or CSV files."""
import csv
import json

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


@app.route('/products')
def products():
    source = request.args.get('source')
    product_id = request.args.get('id')

    if source == 'json':
        data = read_json('products.json')
    elif source == 'csv':
        data = read_csv('products.csv')
    else:
        return render_template('product_display.html', error="Wrong source")

    if product_id is not None:
        try:
            product_id = int(product_id)
        except ValueError:
            return render_template('product_display.html',
                                    error="Product not found")

        data = [product for product in data if product['id'] == product_id]
        if not data:
            return render_template('product_display.html',
                                    error="Product not found")

    return render_template('product_display.html', products=data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
