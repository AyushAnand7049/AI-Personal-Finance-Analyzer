from database import get_db
from services.insights_engine import generate_insights
from services.predictor import predict_next_month
from datetime import datetime
from collections import defaultdict
import json

# Financial knowledge base (RAG simulation - in production, use FAISS )
FINANCE_TIPS = {
    "food": [
        "Meal prep on weekends to cut weekday food delivery costs by up to 60%.",
        "Set a weekly food budget and track it using the 50/30/20 rule.",
        "Cooking at home averages ₹50-100 per meal vs ₹200-400 for delivery.",
        "Use grocery apps like BigBasket for bulk buying discounts.",
        "Limit dining out to 2-3 times per week as a treat, not a habit."
    ],
    "savings": [
        "The 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
        "Automate savings transfers on salary day before spending starts.",
        "Build an emergency fund covering 3-6 months of expenses.",
        "Start a SIP (Systematic Investment Plan) with just ₹500/month.",
        "Small savings compound significantly — ₹1000/month at 12% = ₹23L in 20 years."
    ],
    "subscriptions": [
        "Audit all subscriptions quarterly and cancel unused ones.",
        "Share streaming plans with family members to split costs.",
        "Annual subscription plans typically save 15-30% over monthly.",
        "Use free tiers where possible — Spotify free, YouTube with ad-block.",
        "Track subscriptions in a spreadsheet with renewal dates."
    ],
    "travel": [
        "Book flights 6-8 weeks in advance for best prices.",
        "Use metro/bus instead of cab for daily commutes — saves ₹3000-8000/month.",
        "Carpool apps like BlaBlaCar reduce travel costs significantly.",
        "Track fuel expenses and consider carpooling for office commutes.",
        "Use travel credit cards for cashback on bookings."
    ],
    "bills": [
        "Switch to energy-efficient appliances to reduce electricity bills.",
        "Compare insurance plans annually — you may be overpaying.",
        "Pre-pay loans when possible to reduce interest burden.",
        "Negotiate internet/DTH plans — providers often have unreised offers.",
        "Set bill payment reminders to avoid late fees."
    ],
    "general": [
        "Track every expense — awareness is the first step to saving.",
        "Avoid lifestyle inflation as your income grows.",
        "Pay off high-interest debt (credit cards) before investing.",
        "Review your spending patterns monthly to identify waste.",
        "Set specific financial goals — vague goals don't get achieved."
    ],
    "investment": [
        "Start investing early — time in market beats timing the market.",
        "Diversify: equities, debt, gold, and real estate.",
        "Index funds outperform most actively managed funds long-term.",
        "Maximize tax-saving instruments: PPF, ELSS, NPS (Section 80C).",
        "Review your investment portfolio every 6 months."
    ]
}

def get_user_financial_context() -> dict:
    """Get current user financial summary for AI context"""
    insights = generate_insights()
    prediction = predict_next_month()
    
    with get_db() as conn:
        recent = conn.execute(
            "SELECT category, SUM(amount) as total FROM transactions "
            "WHERE date >= date('now', '-30 days') GROUP BY category ORDER BY total DESC"
        ).fetchall()
    
    return {
        "total_this_month": insights.get("total_spent", 0),
        "top_category": insights.get("top_category", "Unknown"),
        "category_breakdown": insights.get("category_breakdown", {}),
        "predicted_next_month": prediction.get("next_month_total", 0),
        "spending_trend": prediction.get("trend", "stable"),
        "insights": insights.get("insights", [])
    }

def retrieve_relevant_tips(question: str, user_context: dict) -> list:
    """Simple keyword-based retrieval (RAG simulation)"""
    question_lower = question.lower()
    tips = []
    
    keyword_map = {
        "food": ["food", "eat", "restaurant", "swiggy", "zomato", "delivery", "lunch", "dinner"],
        "savings": ["save", "saving", "money", "budget", "afford", "expensive"],
        "subscriptions": ["subscription", "netflix", "streaming", "membership"],
        "travel": ["travel", "cab", "uber", "transport", "commute", "fuel"],
        "bills": ["bill", "electricity", "rent", "insurance", "emi", "loan"],
        "investment": ["invest", "return", "mutual fund", "sip", "stock", "grow"],
        "general": ["overspending", "reduce", "cut", "help", "advice", "tips"]
    }
    
    matched_categories = []
    for category, keywords in keyword_map.items():
        if any(kw in question_lower for kw in keywords):
            matched_categories.append(category)
    
    # Also add tips based on user's top spending category
    top_cat = user_context.get("top_category", "").lower()
    if top_cat in keyword_map:
        matched_categories.append(top_cat)
    
    # Default to general tips
    if not matched_categories:
        matched_categories = ["general", "savings"]
    
    seen = set()
    for cat in matched_categories:
        for tip in FINANCE_TIPS.get(cat, [])[:3]:
            if tip not in seen:
                tips.append(tip)
                seen.add(tip)
    
    return tips[:6]

def build_advisor_prompt(question: str, user_context: dict, tips: list) -> str:
    breakdown = user_context.get("category_breakdown", {})
    breakdown_str = ", ".join([f"{k}: ₹{v:,.0f}" for k, v in breakdown.items()])
    
    tips_str = "\n".join([f"- {t}" for t in tips])
    
    prompt = f"""You are a friendly, expert personal finance advisor for Indian users.

USER'S FINANCIAL DATA (current month):
- Total spent: ₹{user_context['total_this_month']:,.0f}
- Top spending category: {user_context['top_category']}
- Breakdown: {breakdown_str}
- Spending trend: {user_context['spending_trend']}
- Predicted next month: ₹{user_context['predicted_next_month']:,.0f}

RELEVANT FINANCIAL TIPS FROM KNOWLEDGE BASE:
{tips_str}

USER'S QUESTION: {question}

Provide a personalized, actionable answer in 3-4 paragraphs. Reference their actual spending data. Be specific with numbers. Be warm but direct. End with 2-3 concrete action steps they can take today. Use Indian context (₹, Indian apps, Indian financial products like PPF, SIP, etc.)."""
    
    return prompt

async def get_advisor_response(question: str) -> dict:
    """Get AI advisor response using Claude API"""
    import httpx
    
    user_context = get_user_financial_context()
    tips = retrieve_relevant_tips(question, user_context)
    prompt = build_advisor_prompt(question, user_context, tips)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["content"][0]["text"]
            else:
                # Fallback response if API not configured
                answer = generate_fallback_response(question, user_context, tips)
    except Exception as e:
        answer = generate_fallback_response(question, user_context, tips)
    
    return {
        "answer": answer,
        "relevant_data": {
            "monthly_total": user_context["total_this_month"],
            "top_category": user_context["top_category"],
            "trend": user_context["spending_trend"]
        },
        "tips": tips[:3]
    }

def generate_fallback_response(question: str, user_context: dict, tips: list) -> str:
    """Fallback response when API is unavailable"""
    total = user_context.get("total_this_month", 0)
    top_cat = user_context.get("top_category", "general expenses")
    trend = user_context.get("spending_trend", "stable")
    
    response = f"""Based on your financial data, here's my analysis:

Your current monthly spending is ₹{total:,.0f} with {top_cat} as your largest expense category. Your spending trend is currently {trend}.

Here are personalized recommendations based on your question "{question}":

"""
    for i, tip in enumerate(tips[:3], 1):
        response += f"{i}. {tip}\n"
    
    response += f"\nWith your spending pattern, focusing on reducing {top_cat} costs could have the biggest impact on your savings."
    
    return response
