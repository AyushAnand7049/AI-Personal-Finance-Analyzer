"""Seed the database with realistic sample transactions"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, get_db
from services.categorizer import categorize_transaction
from datetime import datetime, timedelta
import random

SAMPLE_TRANSACTIONS = [
    # Food
    ("Swiggy order - Biryani", 380), ("Zomato - Pizza", 450), ("McDonald's", 320),
    ("Chai Sutta Bar", 120), ("BigBasket groceries", 1850), ("Zepto milk & bread", 280),
    ("Restaurant dinner", 1200), ("Coffee - Starbucks", 480), ("Blinkit vegetables", 420),
    ("Dominos pizza", 540),
    # Travel
    ("Uber cab to airport", 650), ("Ola auto", 85), ("Metro card recharge", 200),
    ("IndiGo flight tickets", 4500), ("Rapido bike", 55), ("IRCTC train ticket", 850),
    ("Petrol - BPCL", 2000), ("MakeMyTrip hotel", 3200), ("Parking fee", 40),
    # Bills
    ("Airtel postpaid bill", 599), ("Jio recharge", 239), ("Electricity bill BESCOM", 1240),
    ("Rent transfer", 15000), ("Housing society maintenance", 2500), ("Gas cylinder", 950),
    ("Internet - ACT Fibernet", 799), ("Insurance premium LIC", 3000),
    # Shopping
    ("Amazon purchase", 1299), ("Myntra clothes", 2499), ("Flipkart electronics", 3999),
    ("Croma headphones", 1500), ("Nykaa skincare", 899), ("Ajio shoes", 1799),
    # Entertainment
    ("Netflix subscription", 649), ("Spotify premium", 119), ("BookMyShow movies", 560),
    ("Amazon Prime", 299), ("Hotstar annual plan", 149), ("PVR cinema", 430),
    # Healthcare
    ("Apollo pharmacy", 780), ("1mg medicines", 450), ("Cult.fit gym", 1800),
    ("Doctor consultation", 500), ("Medplus pharmacy", 320),
    # Education
    ("Udemy course", 499), ("Coursera subscription", 1000), ("Books - Amazon", 650),
    # Subscriptions
    ("Adobe Creative Cloud", 1675), ("GitHub Pro", 412), ("Notion", 165),
]

def seed_database():
    init_db()
    
    # Generate 3 months of data
    today = datetime.now()
    
    with get_db() as conn:
        # Clear existing seed data
        conn.execute("DELETE FROM transactions")
        
        inserted = 0
        for month_offset in range(3, -1, -1):
            month_date = today - timedelta(days=30 * month_offset)
            
            # Random subset per month
            month_txns = random.sample(SAMPLE_TRANSACTIONS, min(25, len(SAMPLE_TRANSACTIONS)))
            
            for desc, base_amount in month_txns:
                # Add realistic variance
                amount = base_amount * random.uniform(0.85, 1.2)
                amount = round(amount, 2)
                
                # Random day in that month
                day_offset = random.randint(0, 28)
                tx_date = (month_date.replace(day=1) + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                
                category, confidence = categorize_transaction(desc)
                
                conn.execute(
                    """INSERT INTO transactions (date, description, amount, category, predicted_category, confidence)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (tx_date, desc, amount, category, category, confidence)
                )
                inserted += 1
    
    print(f"✅ Seeded {inserted} sample transactions across 4 months")

if __name__ == "__main__":
    seed_database()
