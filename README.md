# 💰 FinSight AI — Personal Finance Analyzer

> AI-powered expense tracker + financial advisor combining ML, NLP, and personalized insights.

![Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)
![Stack](https://img.shields.io/badge/DB-SQLite-003B57?style=flat-square)
![Stack](https://img.shields.io/badge/AI-Claude%20API-7C6CFC?style=flat-square)
![Stack](https://img.shields.io/badge/Frontend-Vanilla%20JS-F0DB4F?style=flat-square)

---

## 🏗️ Architecture

```
finance-analyzer/
├── backend/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── database.py                # SQLite connection + schema
│   ├── seed.py                    # Sample data generator
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   ├── routes/
│   │   ├── transactions.py        # POST /transaction, GET, DELETE, CSV upload
│   │   ├── insights.py            # GET /insights
│   │   ├── prediction.py          # GET /prediction
│   │   └── advisor.py             # POST /ask
│   └── services/
│       ├── categorizer.py         # ML keyword-based categorization
│       ├── insights_engine.py     # Pattern detection + insight generation
│       ├── predictor.py           # Linear regression forecasting
│       └── advisor.py             # RAG-style AI advisor (Claude API)
└── frontend/
    └── index.html                 # Full SPA dashboard
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Seed with sample data (optional but recommended)
python seed.py

# Start the API server
python main.py
# → API running at http://localhost:8000
# → Swagger docs at http://localhost:8000/docs
```

### 2. Frontend

Open `frontend/index.html` directly in your browser:

```bash
# Option 1: Direct open
open frontend/index.html

# Option 2: Serve with Python (avoids CORS issues)
cd frontend
python -m http.server 3000
# → Open http://localhost:3000
```

### 3. Configure AI Advisor (Optional)

Add your Anthropic API key to use Claude as the advisor:

```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-key-here"
```

Or create a `.env` file in `backend/`:
```
ANTHROPIC_API_KEY=your-key-here
```

> Without an API key, the advisor uses rule-based fallback responses.

---

## 📡 API Reference

### `POST /transaction/`
Add a single transaction. AI auto-categorizes if no category provided.

```json
{
  "date": "2024-01-15",
  "description": "Swiggy Biryani",
  "amount": 380,
  "category": null
}
```

**Response:**
```json
{
  "id": 1,
  "category": "Food",
  "confidence": 0.95
}
```

---

### `GET /transaction/`
Fetch all transactions. Supports `?limit=50&offset=0`.

---

### `POST /transaction/upload-csv`
Bulk import from CSV. Required columns: `date`, `description`, `amount`.

---

### `GET /insights/`
AI-generated insights based on current month spending.

```json
{
  "total_spent": 24500.0,
  "top_category": "Food",
  "insights": [
    "You spent 15% more this month compared to last month",
    "Your biggest expense category is Food at ₹8,200 (33.5%)",
    "⚠️ Your Food spending increased by 35.2% this month"
  ],
  "category_breakdown": { "Food": 8200, "Bills": 6000, ... },
  "month_over_month": { "2024-01": 22000, "2024-02": 24500 }
}
```

---

### `GET /prediction/`
Next month forecast using linear regression on historical data.

```json
{
  "next_month_total": 26800.0,
  "by_category": { "Food": 9200, "Bills": 6200, ... },
  "confidence": "high",
  "trend": "increasing",
  "prediction_month": "March 2024",
  "months_analyzed": 4
}
```

---

### `POST /ask/`
Ask the AI financial advisor a question.

```json
{ "question": "How can I reduce my food expenses?" }
```

**Response:**
```json
{
  "answer": "Based on your spending data, food is your largest expense at ₹8,200...",
  "relevant_data": { "monthly_total": 24500, "top_category": "Food", "trend": "increasing" },
  "tips": ["Meal prep on weekends...", "Use grocery apps for bulk discounts..."]
}
```

---

## 🧠 ML & AI Components

### 1. Expense Categorization
- **Approach:** Keyword-based scoring with confidence estimation
- **Categories:** Food, Travel, Bills, Shopping, Entertainment, Healthcare, Education, Subscriptions
- **Confidence levels:** High (≥95%), Medium (80%), Low (65%)
- **Upgrade path:** Replace with `sentence-transformers` for semantic classification

### 2. Spending Prediction
- **Algorithm:** Ordinary Least Squares (OLS) linear regression
- **Scope:** Per-category + total monthly forecast
- **Confidence:** Based on number of months of data available
- **Upgrade path:** Implement ARIMA or Prophet for time series

### 3. Insight Engine
- Month-over-month comparison
- Category spike/drop detection
- Daily average + month projection
- Subscription growth tracking

### 4. RAG-based AI Advisor
- **Knowledge base:** Curated Indian personal finance tips
- **Retrieval:** Keyword similarity to match question → tips
- **Generation:** Claude API with user's actual financial data injected into prompt
- **Upgrade path:** Replace retrieval with FAISS + LangChain for true vector RAG

---

## 📂 CSV Format

```csv
date,description,amount
2024-01-15,Swiggy Biryani,380
2024-01-16,Uber to office,120
2024-01-17,Netflix subscription,649
```

Also works with bank exports using columns like `narration`, `debit`, etc.

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| Database | SQLite (via stdlib) |
| ML | Pure Python (OLS regression) |
| AI | Claude API (claude-sonnet-4) |
| Frontend | Vanilla JS + Chart.js |
| Styling | CSS custom properties |

---

## 🚀 Production Upgrades

1. **Categorization:** Fine-tune `distilbert` on expense data
2. **Prediction:** Use `prophet` or `statsmodels` ARIMA
3. **RAG:** Implement FAISS + LangChain with a real finance document corpus
4. **Auth:** Add JWT authentication
5. **DB:** Migrate to PostgreSQL for multi-user support
6. **Deploy:** Docker + Railway/Render/AWS

---

## 📊 Sample Data

Run `python seed.py` to populate 4 months of realistic Indian expense data (100 transactions) covering all categories.

---

*Built with FastAPI + SQLite + Claude AI*
