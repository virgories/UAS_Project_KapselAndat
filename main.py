from fastapi import FastAPI
from .database import engine, Base
from .routers import categories, transaction, analytics, analytics_category, data_uas_router

app = FastAPI()

# Categories -> pakai prefix dari router saja
app.include_router(categories.router)

# Transaction / lainnya -> sama, jangan didobel prefix lagi
app.include_router(data_uas_router.router)
app.include_router(transaction.router)
app.include_router(analytics.router)
app.include_router(analytics_category.router)

