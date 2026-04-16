from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, oauth2
from ..services import report_service, advice_service

router = APIRouter(prefix="/report", tags=["Report"])

@router.get("/summary")
def get_summary(db: Session = Depends(database.get_db),
                user=Depends(oauth2.get_current_user)):

    expenses = db.query(models.Expense).filter(models.Expense.owner_id == user.id).all()
    incomes = db.query(models.Income).filter(models.Income.owner_id == user.id).all()

    report = report_service.generate_report(expenses, incomes)
    advice = advice_service.generate_advice(expenses, incomes)

    return {
        "report": report,
        "advice": advice
    }