#!/bin/bash

if [ -f coupon.db ]; then
    rm coupon.db
fi

echo "-------------------"
python app.py add_coupon coupon_1 5 ''
python app.py test_product coupon_1 '{"name": "cake", "price": 10, "category": "food"}'
echo "Expected - Applicable, new price is: 5"

echo "-------------------"
python app.py add_coupon coupon_2 20% ''
python app.py test_product coupon_2 '{"name": "cake", "price": 10, "category": "food"}'
echo "Expected - Applicable, new price is: 8.0"

echo "-------------------"
python app.py add_coupon coupon_3 5 '{"category": "food"}'
python app.py test_product coupon_3 '{"name": "cake", "price": 10, "category": "food"}'
echo "Expected - Applicable, new price is: 5"

echo "-------------------"
python app.py add_coupon coupon_4 20 '{"category": "food"}'
python app.py test_product coupon_4 '{"name": "table", "price": 100, "category": "furniture"}'
echo "Expected - Not applicable"

echo "-------------------"
python app.py add_coupon coupon_5 20 '{"price_above": 100}'
python app.py test_product coupon_5 '{"name": "table", "price": 100, "category": "furniture"}'
echo "Expected - Not applicable"

echo "-------------------"
python app.py add_coupon coupon_6 20 '{"price_above": 50}'
python app.py test_product coupon_6 '{"name": "table", "price": 100, "category": "furniture"}'
echo "Expected - Applicable, new price is: 80"

echo "-------------------"
python app.py add_coupon coupon_7 20 '{"price_above": 150}'
python app.py test_product coupon_7 '{"name": "table", "price": 100, "category": "furniture"}'
echo "Expected - Not applicable"

echo "-------------------"
python app.py add_coupon coupon_8 20 '{"date_in_range": "2022-01-01,2026-01-01"}'
python app.py test_product coupon_8 '{"name": "table", "price": 100, "category": "furniture"}'
echo "Expected - Applicable, new price is: 80"

echo "-------------------"
python app.py add_coupon coupon_9 20 '{"date_in_range": "2022-01-01,2022-01-02"}'
python app.py test_product coupon_9 '{"name": "table", "price": 100, "category": "furniture"}'
echo "Expected - Not applicable"

echo "-------------------"
python app.py add_coupon coupon_10 5 '{"category": "cloth"}'
echo "Expected - Error"

echo "-------------------"
python app.py add_coupon coupon_11 5 '{"price_above": "10"}'
echo "Expected - Error"

echo "-------------------"
python app.py add_coupon coupon_12 5 '{"date_in_range": "01-01-2022,01-01-2022"}'
echo "Expected - Error"