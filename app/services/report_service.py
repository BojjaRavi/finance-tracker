# report_service.py
def generate_report(expenses, incomes):
    total_expense = sum(e.amount for e in expenses)
    total_income = sum(i.amount for i in incomes)

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "savings": total_income - total_expense
    }