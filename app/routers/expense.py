# expense.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, database, oauth2

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/")
def create_expense(expense: schemas.ExpenseCreate,
                   db: Session = Depends(database.get_db),
                   user=Depends(oauth2.get_current_user)):

    new_expense = models.Expense(**expense.dict(), owner_id=user.id)

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


@router.get("/")
def get_expenses(db: Session = Depends(database.get_db),
                 user=Depends(oauth2.get_current_user)):

    return db.query(models.Expense).filter(models.Expense.owner_id == user.id).all()