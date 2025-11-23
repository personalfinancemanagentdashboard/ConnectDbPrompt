from app import db
from models.transaction import Transaction
from sqlalchemy import func


def get_ai_insights(user_id):
    insights = []
    
    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'income'
    ).scalar() or 0.0
    
    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense'
    ).scalar() or 0.0
    
    if total_expense > total_income:
        insights.append({
            'type': 'warning',
            'message': 'High spending alert! Your expenses exceed your income.',
            'icon': '⚠️'
        })
    elif total_income > total_expense:
        savings = total_income - total_expense
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        insights.append({
            'type': 'success',
            'message': f'Great job! You\'re saving ${savings:.2f} ({savings_rate:.1f}% of income).',
            'icon': '✅'
        })
    
    category_data = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense'
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    
    if category_data:
        top_category = category_data[0]
        insights.append({
            'type': 'info',
            'message': f'Your top spending category is "{top_category[0]}" with ${top_category[1]:.2f}.',
            'icon': '📊'
        })
    
    transaction_count = Transaction.query.filter_by(user_id=user_id).count()
    
    if transaction_count == 0:
        insights.append({
            'type': 'info',
            'message': 'Start tracking your finances by adding your first transaction!',
            'icon': '🚀'
        })
    elif transaction_count < 5:
        insights.append({
            'type': 'info',
            'message': 'Add more transactions to get better financial insights.',
            'icon': '💡'
        })
    
    if total_income > 0 and total_expense > 0:
        expense_ratio = (total_expense / total_income * 100)
        if expense_ratio < 50:
            insights.append({
                'type': 'success',
                'message': f'Excellent! You\'re only spending {expense_ratio:.1f}% of your income.',
                'icon': '🌟'
            })
        elif expense_ratio > 90:
            insights.append({
                'type': 'warning',
                'message': f'You\'re spending {expense_ratio:.1f}% of your income. Consider reducing expenses.',
                'icon': '💰'
            })
    
    if not insights:
        insights.append({
            'type': 'info',
            'message': 'Keep tracking your transactions for personalized insights!',
            'icon': '📈'
        })
    
    return insights
