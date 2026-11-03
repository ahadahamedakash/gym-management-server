from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import auth, subscriptions, enrollments

app = FastAPI(
    title="Gym Management API",
    summary="API for gym subscription management",
    description=("Manage gym subscriptions, users, " "and enrollments."),
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://gym-management-client-delta.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(enrollments.router)


@app.get("/", include_in_schema=False)
def home():
    return {"message": "Server is up and running!"}
