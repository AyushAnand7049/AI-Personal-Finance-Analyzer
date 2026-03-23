from database import get_db
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import math

def get_all_monthly_data() -> Dict[str, Dict[str, float]]:
    """Get spending grouped by month and category"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT date, category, amount FROM transactions ORDER BY date"
        ).fetchall()
    
    monthly_cat = defaultdict(lambda: defaultdict(float))
    for row in rows:
        month_key = row["date"][:7]
        monthly_cat[month_key][row["category"]] += row["amount"]
    
    return {k: dict(v) for k, v in monthly_cat.items()}

def simple_linear_regression(x_vals, y_vals) -> Tuple[float, float]:
    """Calculate slope and intercept for linear regression"""
    n = len(x_vals)
    if n < 2:
        return 0, y_vals[0] if y_vals else 0
    
    x_mean = sum(x_vals) / n
    y_mean = sum(y_vals) / n
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, y_vals))
    denominator = sum((x - x_mean) ** 2 for x in x_vals)
    
    if denominator == 0:
        return 0, y_mean
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return slope, intercept

def predict_next_month() -> dict:
    monthly_data = get_all_monthly_data()
    
    if len(monthly_data) < 2:
        return {
            "next_month_total": 0,
            "by_category": {},
            "confidence": "low",
            "trend": "insufficient data",
            "message": "Add at least 2 months of data for predictions"
        }
    
    sorted_months = sorted(monthly_data.keys())
    
    # Predict by category
    all_categories = set()
    for month_cats in monthly_data.values():
        all_categories.update(month_cats.keys())
    
    predictions_by_cat = {}
    
    for category in all_categories:
        y_vals = []
        x_vals = []
        for i, month in enumerate(sorted_months):
            amount = monthly_data[month].get(category, 0)
            y_vals.append(amount)
            x_vals.append(i)
        
        if sum(y_vals) == 0:
            continue
        
        slope, intercept = simple_linear_regression(x_vals, y_vals)
        next_x = len(sorted_months)
        predicted = intercept + slope * next_x
        predicted = max(0, predicted)  # no negative spending
        predictions_by_cat[category] = round(predicted, 2)
    
    # Total spending trend
    monthly_totals = [sum(monthly_data[m].values()) for m in sorted_months]
    x_vals = list(range(len(monthly_totals)))
    slope, intercept = simple_linear_regression(x_vals, monthly_totals)
    
    next_total = intercept + slope * len(monthly_totals)
    next_total = max(0, next_total)
    
    # Determine trend direction
    if len(monthly_totals) >= 3:
        recent_avg = sum(monthly_totals[-3:]) / 3
        older_avg = sum(monthly_totals[:-3]) / max(len(monthly_totals) - 3, 1)
        if recent_avg > older_avg * 1.1:
            trend = "increasing"
        elif recent_avg < older_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # Confidence based on data points
    n_months = len(sorted_months)
    if n_months >= 6:
        confidence = "high"
    elif n_months >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Calculate month-over-month variance
    if len(monthly_totals) > 1:
        mean_total = sum(monthly_totals) / len(monthly_totals)
        variance = sum((t - mean_total) ** 2 for t in monthly_totals) / len(monthly_totals)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 0
    
    next_month_name = get_next_month_name()
    
    return {
        "next_month_total": round(next_total, 2),
        "by_category": predictions_by_cat,
        "confidence": confidence,
        "trend": trend,
        "std_deviation": round(std_dev, 2),
        "prediction_month": next_month_name,
        "months_analyzed": n_months,
        "historical_average": round(sum(monthly_totals) / len(monthly_totals), 2) if monthly_totals else 0
    }

def get_next_month_name() -> str:
    now = datetime.now()
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)
    return next_month.strftime("%B %Y")
