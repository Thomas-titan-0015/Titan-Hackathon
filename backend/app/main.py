import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.db.database import engine
from app.db import Base
from app.routers import products, cart, wishlist, chat, dashboard, orders
from app.routers.auth import router as auth_router
from app.services import openai_service

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "pure-api-x8k2m9p4q7w3")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tanishq — Luxury Jewelry", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API key middleware — protects all /api/ routes
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        key = request.headers.get("x-api-key")
        if key != API_SECRET_KEY:
            return JSONResponse(status_code=403, content={"detail": "Forbidden: invalid API key"})
    response = await call_next(request)
    return response


# Routers
app.include_router(auth_router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(wishlist.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(orders.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def startup():
    openai_service.init()
    from app.seed import seed_database
    seed_database()


# Serve frontend (must be last)
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
