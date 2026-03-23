#!/bin/bash
echo "🚀 Starting FinSight AI Finance Analyzer"
echo ""

# Start backend
echo "📦 Starting FastAPI backend..."
cd "$(dirname "$0")/backend"

# Install deps if needed
if ! python -c "import fastapi" 2>/dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt -q
fi

# Seed if DB empty
python -c "
import sys; sys.path.insert(0,'.')
from database import init_db, get_db
init_db()
with get_db() as conn:
    count = conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]
if count == 0:
    print('Seeding sample data...')
    from seed import seed_database
    seed_database()
else:
    print(f'Database has {count} transactions')
"

# Start server
echo ""
echo "✅ Backend starting at http://localhost:8000"
echo "📖 API docs at http://localhost:8000/docs"
echo ""
echo "👉 Open frontend/index.html in your browser"
echo ""
python main.py &
BACKEND_PID=$!

# Serve frontend
echo "🌐 Serving frontend at http://localhost:3000"
cd ../frontend
python -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "Press Ctrl+C to stop all services"
wait
