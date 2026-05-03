# FinSight AI — Personal Finance Analyzer

## Architecture

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

# Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
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

Open `frontend/index.html`

```bash
# Option 1: Direct open
open frontend/index.html

# Option 2: Serve with Python (avoids CORS issues)
cd frontend
python -m http.server 3000
# → Open http://localhost:3000
```

### 3. Configure AI Advisor 

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

