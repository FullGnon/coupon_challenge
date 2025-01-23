from coupon_challenge.routers import coupons
from fastapi import FastAPI

app = FastAPI()
app.include_router(coupons.router)
