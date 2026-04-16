# budget.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, database, oauth2

router = APIRouter(prefix="/budget", tags=["Budget"])


@router.post("/")
def create_budget(budget: schemas.BudgetCreate,
                  db: Session = Depends(database.get_db),
                  user=Depends(oauth2.get_current_user)):

    new_budget = models.Budget(**budget.dict(), owner_id=user.id)

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget