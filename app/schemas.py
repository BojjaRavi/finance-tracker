# schemas.py
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str


class ExpenseCreate(BaseModel):
    amount: float
    category_id: int


class IncomeCreate(BaseModel):
    amount: float


class CategoryCreate(BaseModel):
    name: str
    type: str


class BudgetCreate(BaseModel):
    total_amount: float
    period: str