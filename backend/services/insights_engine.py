from database import get_db
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple
import statistics

def get_current_month_data() -> List[dict]:
    now = datetime.now()
    month_str = f"{now.year}-{now.month:02d}"
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE date LIKE ? ORDER BY date DESC",
            (f"{month_str}%",)
        ).fetchall()
    return [dict(r) for r in rows]

def get_last_n_months(n: int = 6) -> List[dict]:
    cutoff = (datetime.now() - timedelta(days=30 * n)).strftime("%Y-%m-%d")
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE date >= ? ORDER BY date",
            (cutoff,)
        ).fetchall()
    return [dict(r) for r in rows]

def group_by_category(transactions: List[dict]) -> Dict[str, float]:
    totals = defaultdict(float)
    for tx in transactions:
        totals[tx["category"]] += tx["amount"]
    return dict(totals)

def group_by_month(transactions: List[dict]) -> Dict[str, float]:
    monthly = defaultdict(float)
    for tx in transactions:
        month_key = tx["date"][:7]  # YYYY-MM
        monthly[month_key] += tx["amount"]
    return dict(sorted(monthly.items()))

def generate_insights() -> dict:
    all_transactions = get_last_n_months(6)
    current_month_txns = get_current_month_data()
    
    now = datetime.now()
    last_month_str = f"{now.year}-{now.month - 1:02d}" if now.month > 1 else f"{now.year - 1}-12"
    
    last_month_txns = [t for t in all_transactions if t["date"].startswith(last_month_str)]
    
    current_by_cat = group_by_category(current_month_txns)
    last_by_cat = group_by_category(last_month_txns)
    
    total_current = sum(current_by_cat.values())
    total_last = sum(last_by_cat.values())
    
    monthly_totals = group_by_month(all_transactions)
    
    insights = []

    # Insight 1: Month-over-month total change
    if total_last > 0:
        pct_change = ((total_current - total_last) / total_last) * 100
        direction = "more" if pct_change > 0 else "less"
        insights.append(
            f"You spent {abs(pct_change):.1f}% {direction} this month compared to last month "
            f"(₹{total_current:,.0f} vs ₹{total_last:,.0f})"
        )

    # Insight 2: Top spending category
    if current_by_cat:
        top_cat = max(current_by_cat, key=current_by_cat.get)
        top_pct = (current_by_cat[top_cat] / total_current * 100) if total_current > 0 else 0
        insights.append(
            f"Your biggest expense category is {top_cat} at ₹{current_by_cat[top_cat]:,.0f} ({top_pct:.1f}% of total)"
        )

    # Insight 3: Category spikes
    for cat, current_amt in current_by_cat.items():
        last_amt = last_by_cat.get(cat, 0)
        if last_amt > 0:
            change = ((current_amt - last_amt) / last_amt) * 100
            if change > 30:
                insights.append(
                    f"⚠️ Your {cat} spending increased by {change:.1f}% this month (₹{last_amt:,.0f} → ₹{current_amt:,.0f})"
                )
            elif change < -20:
                insights.append(
                    f"✅ Great job! You cut {cat} spending by {abs(change):.1f}% this month"
                )

    # Insight 4: Subscription tracking
    sub_amount = current_by_cat.get("Subscriptions", 0)
    if sub_amount > 0:
        last_sub = last_by_cat.get("Subscriptions", 0)
        if sub_amount > last_sub:
            insights.append(f"📱 Your subscription costs rose to ₹{sub_amount:,.0f} this month")

    # Insight 5: Daily average
    days_elapsed = now.day
    if total_current > 0 and days_elapsed > 0:
        daily_avg = total_current / days_elapsed
        projected = daily_avg * 30
        insights.append(
            f"📅 Your daily average spend is ₹{daily_avg:,.0f} — projected month total: ₹{projected:,.0f}"
        )

    # Insight 6: Savings tip
    if total_current > 0 and current_by_cat.get("Food", 0) / total_current > 0.4:
        insights.append("🍽️ Food is over 40% of your budget. Consider meal prepping to reduce costs.")

    top_category = max(current_by_cat, key=current_by_cat.get) if current_by_cat else "N/A"

    return {
        "total_spent": round(total_current, 2),
        "top_category": top_category,
        "insights": insights,
        "category_breakdown": {k: round(v, 2) for k, v in current_by_cat.items()},
        "month_over_month": {k: round(v, 2) for k, v in monthly_totals.items()},
        "transaction_count": len(current_month_txns)
    }
