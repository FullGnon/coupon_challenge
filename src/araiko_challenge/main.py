from fastapi import FastAPI

from araiko_challenge.routers import coupons

app = FastAPI()
app.include_router(coupons.router)
