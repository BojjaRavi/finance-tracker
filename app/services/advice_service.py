# advice_service.py
def generate_advice(expenses, incomes):
    total_expense = sum(e.amount for e in expenses)
    total_income = sum(i.amount for i in incomes)

    if total_income == 0:
        return "No income data"

    ratio = total_expense / total_income

    if ratio > 0.8:
        return "⚠️ High spending! Reduce expenses."
    elif ratio > 0.5:
        return "⚠️ Moderate spending. Follow 50/30/20 rule."
    else:
        return "✅ Good financial discipline!"