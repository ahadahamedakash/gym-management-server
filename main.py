from fastapi import FastAPI

from routers import auth, subscriptions, enrollments

app = FastAPI(
    title="Gym Management API",
    summary="API for gym subscription management",
    description=("Manage gym subscriptions, users, " "and enrollments."),
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(enrollments.router)


@app.get("/", include_in_schema=False)
def home():
    return {"message": "Server is up and running!"}
