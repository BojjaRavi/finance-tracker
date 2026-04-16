# main.py
from fastapi import FastAPI
from .database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, expense, income, category, budget, user, ai

Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = ["*"]  # allow all for now

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(expense.router)
app.include_router(income.router)
app.include_router(category.router)
app.include_router(budget.router)
app.include_router(user.router)
app.include_router(ai.router)


@app.get("/")
def root():
    return {"message": "🚀 Financial Tracker Running"}