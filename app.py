from datetime import datetime
import json
import argparse
import re
import sqlite3

connection = sqlite3.connect("coupon.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS coupon (
    name TEXT UNIQUE PRIMARY KEY,
    discount TEXT,
    condition TEXT
);               
""")
connection.commit()


def add_coupon(args):
    name = args.name
    discount = args.discount
    condition = args.condition

    if condition != '':
        condition = json.loads(condition)

    if condition and (('category' in condition.keys() and condition['category'] not in ['food', 'furniture', 'electronics']) or \
        ('price_above' in condition.keys() and type(condition['price_above']) != int) or \
        ('date_in_range' in condition.keys() and not re.match(r'^\d{4}-\d{2}-\d{2},\d{4}-\d{2}-\d{2}$', condition['date_in_range']))):
        print('Error')
        return
    
    cursor.execute("INSERT INTO coupon VALUES ('%s', '%s', '%s')" % (name, discount, json.dumps(condition)))
    connection.commit()

    print ('Coupon added: name=%s discount=%s condition=%s' % (name, discount, json.dumps(condition)))

def test_product(args):
    coupon_name = args.coupon_name
    product = json.loads(args.product)
    print ('Test coupon "%s" against product:%s' % (coupon_name, json.dumps(product)))
    cursor.execute('SELECT * FROM coupon WHERE name = "%s"' % coupon_name)
    connection.commit()
    coupon = cursor.fetchone()
    condition = json.loads(coupon[2])
    true_conditions = 0
    if not condition == "":
        if 'category' in condition.keys() and condition['category'] == product['category']:
            true_conditions += 1
        if 'price_above' in condition.keys() and condition['price_above'] < product['price']:
            true_conditions += 1

        if 'date_in_range' in condition.keys() and \
            datetime.strptime(condition['date_in_range'].split(',')[0], "%Y-%m-%d") < datetime.now() and \
            datetime.strptime(condition['date_in_range'].split(',')[1], "%Y-%m-%d") > datetime.now():
            true_conditions += 1
    
    if not condition or true_conditions == len(condition.keys()):
        discount = coupon[1]
        if discount[-1] == '%':
            new_price = product['price'] * (1 - int(discount[:-1]) / 100)
        else:
            new_price = product['price'] - int(discount)
        print ('Applicable, new price is: %s' % new_price)
        return
    
    print ('Not applicable')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Coupon Management System')
    subparsers = parser.add_subparsers(help='commands')

    add_coupon_parser = subparsers.add_parser('add_coupon')
    add_coupon_parser.add_argument('name', type=str)
    add_coupon_parser.add_argument('discount', type=str)
    add_coupon_parser.add_argument('condition', type=str)
    add_coupon_parser.set_defaults(func=add_coupon)

    test_product_parser = subparsers.add_parser('test_product')
    test_product_parser.add_argument('coupon_name', type=str)
    test_product_parser.add_argument('product', type=str)
    test_product_parser.set_defaults(func=test_product)

    args = parser.parse_args()
    args.func(args)
