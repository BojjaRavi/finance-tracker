# user.py
from fastapi import APIRouter, Depends
from .. import oauth2

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_me(user=Depends(oauth2.get_current_user)):
    return user