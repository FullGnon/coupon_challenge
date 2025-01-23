from fastapi import FastAPI

from coupon_challenge.routers import coupons

app = FastAPI()
app.include_router(coupons.router)
