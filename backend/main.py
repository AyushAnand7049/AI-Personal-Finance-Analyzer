from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routes.transactions import router as transactions_router
from routes.insights import router as insights_router
from routes.prediction import router as prediction_router
from routes.advisor import router as advisor_router
from database import init_db

app = FastAPI(
    title="AI Personal Finance Analyzer",
    description="AI-powered expense tracker and financial advisor",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

app.include_router(transactions_router, prefix="/transaction", tags=["Transactions"])
app.include_router(insights_router, prefix="/insights", tags=["Insights"])
app.include_router(prediction_router, prefix="/prediction", tags=["Prediction"])
app.include_router(advisor_router, prefix="/ask", tags=["AI Advisor"])

@app.get("/")
def root():
    return {"message": "AI Personal Finance Analyzer API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
