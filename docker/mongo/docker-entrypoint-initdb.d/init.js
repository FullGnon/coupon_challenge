// Insert initial data into a collection
db.coupons.insertMany([
    {name: "coupon_1", discount: 5},
    {name: "coupon_2", discount: "20%"},
    {name: "coupon_3", discount: 5, condition: {"category": "food"}},
    {name: "coupon_4", discount: 20, condition: {"category": "food"}},
    {name: "coupon_5", discount: 20, condition: {"price_above": 100}},
    {name: "coupon_6", discount: 20, condition: {"price_above": 50}},
    {name: "coupon_7", discount: 20, condition: {"price_above": 150}},
    {name: "coupon_8", discount: 20, validity: {"start": "2022-01-01", "end": "2026-01-01"}},
    {name: "coupon_9", discount: 20, validity: {"start": "2022-01-01", "end": "2022-01-01"}},
]);
