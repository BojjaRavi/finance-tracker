"""
AI Financial Advisor Service using Google Gemini API
Provides intelligent spending analysis and financial recommendations
"""

import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Expense, Income, Budget, Category, User
import google.generativeai as genai

# Configure Google Gemini API
def configure_gemini(api_key: str):
    """Configure Gemini API with provided key"""
    genai.configure(api_key=api_key)

def get_financial_summary(db: Session, user_id: int) -> dict:
    """Get comprehensive financial summary for AI analysis"""
    try:
        # Get date range (last 3 months)
        three_months_ago = datetime.now() - timedelta(days=90)
        
        # Expenses by category
        expenses_by_category = db.query(
            Category.name,
            func.sum(Expense.amount).label("total")
        ).join(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= three_months_ago
        ).group_by(Category.name).all()
        
        # Total income and expenses
        total_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.date >= three_months_ago
        ).scalar() or 0
        
        total_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= three_months_ago
        ).scalar() or 0
        
        # Current month data
        current_month_start = datetime.now().replace(day=1)
        current_month_income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.date >= current_month_start
        ).scalar() or 0
        
        current_month_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= current_month_start
        ).scalar() or 0
        
        # Budgets
        budgets = db.query(
            Category.name,
            Budget.limit_amount,
            func.sum(Expense.amount).label("spent")
        ).join(Category).outerjoin(
            Expense,
            (Expense.category_id == Budget.category_id) & 
            (Expense.user_id == Budget.user_id) &
            (func.extract('month', Expense.date) == func.extract('month', datetime.now())) &
            (func.extract('year', Expense.date) == func.extract('year', datetime.now()))
        ).filter(
            Budget.user_id == user_id
        ).group_by(Category.name, Budget.limit_amount).all()
        
        # Highest spending categories
        top_categories = expenses_by_category[:5]
        
        return {
            "total_income_3m": float(total_income),
            "total_expenses_3m": float(total_expenses),
            "current_month_income": float(current_month_income),
            "current_month_expenses": float(current_month_expenses),
            "expenses_by_category": [
                {"category": cat[0], "amount": float(cat[1])}
                for cat in expenses_by_category
            ],
            "top_spending_categories": [
                {"category": cat[0], "amount": float(cat[1])}
                for cat in top_categories
            ],
            "budgets": [
                {
                    "category": budget[0],
                    "limit": float(budget[1]),
                    "spent": float(budget[2]) if budget[2] else 0
                }
                for budget in budgets if budget[1]  # Only include budgets with limits
            ]
        }

async def get_ai_financial_advice(db: Session, user_id: int) -> str:
    """
    Get personalized financial advice from Gemini AI
    Analyzes spending patterns and provides actionable recommendations
    """
    try:
        # Get financial summary
        summary = get_financial_summary(db, user_id)
        
        # Build prompt for AI
        prompt = f"""
        Analyze this financial data and provide 3-4 specific, actionable financial recommendations:
        
        Financial Summary (Last 3 Months):
        - Total Income: ${summary['total_income_3m']:.2f}
        - Total Expenses: ${summary['total_expenses_3m']:.2f}
        - Balance: ${summary['total_income_3m'] - summary['total_expenses_3m']:.2f}
        
        Current Month:
        - Income: ${summary['current_month_income']:.2f}
        - Expenses: ${summary['current_month_expenses']:.2f}
        
        Expenses by Category:
        {format_categories(summary['expenses_by_category'])}
        
        Top Spending Categories:
        {format_categories(summary['top_spending_categories'])}
        
        Budgets:
        {format_budgets(summary['budgets'])}
        
        Based on this data, provide:
        1. One observation about their spending pattern
        2. Two specific actionable recommendations
        3. One positive insight about their financial habits
        
        Keep recommendations practical and focused on areas where they can save money or improve financial health.
        Format as clear bullet points.
        """
        
        # Call Gemini API
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        return f"Unable to generate AI advice at this time. Error: {str(e)}"

def format_categories(categories: list) -> str:
    """Format categories for AI prompt"""
    if not categories:
        return "No spending data available"
    return "\n".join([f"- {cat['category']}: ${cat['amount']:.2f}" for cat in categories])

def format_budgets(budgets: list) -> str:
    """Format budgets for AI prompt"""
    if not budgets:
        return "No budgets set"
    result = []
    for budget in budgets:
        spent = budget['spent']
        limit = budget['limit']
        percentage = (spent / limit * 100) if limit > 0 else 0
        status = "⚠️ Over budget" if percentage > 100 else "✅ On track" if percentage > 80 else "✅ Good"
        result.append(f"- {budget['category']}: ${spent:.2f}/${limit:.2f} ({percentage:.0f}%) {status}")
    return "\n".join(result)

async def get_spending_forecast(db: Session, user_id: int, months_ahead: int = 1) -> dict:
    """Predict spending for next N months based on patterns"""
    try:
        # Get last 3 months average spending
        three_months_ago = datetime.now() - timedelta(days=90)
        historical_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= three_months_ago
        ).scalar() or 0
        
        # Calculate average daily spending
        days = 90
        daily_average = historical_expenses / days if days > 0 else 0
        
        # Project forward
        projected_month_spending = daily_average * 30
        
        summary = get_financial_summary(db, user_id)
        
        prompt = f"""
        Based on this spending forecast, provide brief financial guidance:
        
        Historical Average Monthly Spending: ${projected_month_spending:.2f}
        Current Income (Monthly): ${summary['current_month_income']:.2f}
        
        Provide one sentence prediction and one recommendation for next month.
        Keep it concise and actionable.
        """
        
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
        return {
            "forecast_monthly_spending": float(projected_month_spending),
            "recommendation": response.text
        }
    
    except Exception as e:
        return {
            "forecast_monthly_spending": 0,
            "recommendation": f"Unable to generate forecast: {str(e)}"
        }
