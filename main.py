from fastapi import FastAPI
from router import router as email_router

app = FastAPI(title="Email classification")
app.include_router(email_router)
