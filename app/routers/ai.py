"""
AI Advisor Router
Endpoints for AI-powered financial advice and analysis
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.oauth2 import get_current_active_user
from app.models import User
from app.services.ai_advisor_service import get_ai_financial_advice, get_spending_forecast
import os

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/advice")
async def get_advice(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized AI financial advice based on spending patterns
    Uses Google Gemini API to analyze financial data
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="AI service not configured. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        advice = await get_ai_financial_advice(db, current_user.id)
        return {"advice": advice}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating advice: {str(e)}"
        )

@router.get("/forecast")
async def get_forecast(
    months_ahead: int = 1,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered spending forecast for upcoming months
    Analyzes historical patterns and trends
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="AI service not configured. Please set GEMINI_API_KEY environment variable."
        )
    
    if months_ahead < 1 or months_ahead > 12:
        raise HTTPException(
            status_code=400,
            detail="months_ahead must be between 1 and 12"
        )
    
    try:
        forecast = await get_spending_forecast(db, current_user.id, months_ahead)
        return forecast
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating forecast: {str(e)}"
        )
