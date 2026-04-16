# category.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database, oauth2

from .. import models, schemas, database

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(category: schemas.CategoryCreate,
                    db: Session = Depends(database.get_db),
                    user=Depends(oauth2.get_current_user) ):

    new_category = models.Category(**category.dict())  

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.get("/")
def get_categories(db: Session = Depends(database.get_db)):
    return db.query(models.Category).all()