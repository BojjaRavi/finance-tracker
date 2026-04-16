# income.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, database, oauth2

router = APIRouter(prefix="/income", tags=["Income"])


@router.post("/")
def create_income(income: schemas.IncomeCreate,
                  db: Session = Depends(database.get_db),
                  user=Depends(oauth2.get_current_user)):

    new_income = models.Income(**income.dict(), owner_id=user.id)

    db.add(new_income)
    db.commit()
    db.refresh(new_income)

    return new_income