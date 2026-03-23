import re
from typing import Tuple

# Keyword-based categorization rules (lightweight, no heavy ML deps)
CATEGORY_RULES = {
    "Food": [
        "swiggy", "zomato", "restaurant", "cafe", "food", "pizza", "burger",
        "coffee", "tea", "biryani", "hotel", "eat", "lunch", "dinner", "breakfast",
        "snack", "grocery", "vegetables", "fruit", "meat", "bakery", "juice",
        "mcdonald", "kfc", "dominos", "subway", "milk", "dairy", "supermarket",
        "dmart", "bigbasket", "zepto", "blinkit", "instamart"
    ],
    "Travel": [
        "uber", "ola", "rapido", "taxi", "cab", "auto", "bus", "train", "flight",
        "irctc", "makemytrip", "goibibo", "airport", "metro", "petrol", "fuel",
        "toll", "parking", "travel", "trip", "booking", "hotel", "airbnb",
        "indigo", "airindia", "spicejet", "redbus"
    ],
    "Bills": [
        "electricity", "water", "gas", "rent", "internet", "wifi", "broadband",
        "airtel", "jio", "vodafone", "bsnl", "postpaid", "bill", "recharge",
        "dth", "cable", "maintenance", "society", "emi", "loan", "insurance",
        "premium", "tax", "municipal"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "meesho", "ajio", "nykaa", "shopping",
        "cloth", "shirt", "pant", "shoe", "dress", "fashion", "apparel",
        "electronics", "mobile", "laptop", "gadget", "furniture", "home decor",
        "croma", "reliance digital", "walmart", "store"
    ],
    "Entertainment": [
        "netflix", "prime", "hotstar", "youtube", "spotify", "apple music",
        "movie", "cinema", "theatre", "pvr", "inox", "gaming", "steam",
        "concert", "event", "show", "subscription", "zee5", "sonyliv",
        "bookmyshow", "game", "play", "fun"
    ],
    "Healthcare": [
        "pharmacy", "medicine", "hospital", "clinic", "doctor", "health",
        "medical", "apollo", "medplus", "netmeds", "1mg", "pharmeasy",
        "diagnostic", "lab", "test", "surgery", "dental", "eye", "gym",
        "fitness", "yoga", "wellness"
    ],
    "Education": [
        "school", "college", "university", "course", "udemy", "coursera",
        "book", "stationery", "pen", "notebook", "tuition", "coaching",
        "class", "training", "certificate", "exam", "fee", "library"
    ],
    "Subscriptions": [
        "subscription", "monthly plan", "annual plan", "membership",
        "adobe", "microsoft", "google", "icloud", "dropbox", "slack",
        "zoom", "notion", "figma", "github", "aws", "azure"
    ]
}

def categorize_transaction(description: str) -> Tuple[str, float]:
    """
    Categorize a transaction description using keyword matching.
    Returns (category, confidence_score)
    """
    desc_lower = description.lower()
    
    scores = {}
    for category, keywords in CATEGORY_RULES.items():
        score = 0
        matches = 0
        for keyword in keywords:
            if keyword in desc_lower:
                # Exact word match scores higher
                if re.search(r'\b' + re.escape(keyword) + r'\b', desc_lower):
                    score += 2
                else:
                    score += 1
                matches += 1
        if score > 0:
            scores[category] = score
    
    if not scores:
        return "Other", 0.4
    
    best_category = max(scores, key=scores.get)
    max_score = scores[best_category]
    
    # Normalize confidence
    if max_score >= 4:
        confidence = 0.95
    elif max_score >= 2:
        confidence = 0.80
    else:
        confidence = 0.65
    
    return best_category, confidence

def batch_categorize(transactions: list) -> list:
    """Categorize a list of transactions"""
    results = []
    for tx in transactions:
        category, confidence = categorize_transaction(tx.get("description", ""))
        results.append({
            **tx,
            "predicted_category": category,
            "confidence": confidence,
            "category": category
        })
    return results
