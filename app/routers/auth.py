# auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from .. import models, database, utils, oauth2

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: OAuth2PasswordRequestForm = Depends(),
             db: Session = Depends(database.get_db)):

    hashed_pw = utils.hash(user.password)

    new_user = models.User(email=user.username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "User created"}


@router.post("/login")
def login(user: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(database.get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.username).first()

    if not db_user or not utils.verify(user.password, db_user.password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")

    token = oauth2.create_access_token({"user_id": db_user.id})

    return {"access_token": token, "token_type": "bearer"}