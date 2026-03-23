from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class TransactionCreate(BaseModel):
    date: str = Field(..., example="2024-01-15")
    description: str = Field(..., example="Swiggy order")
    amount: float = Field(..., gt=0, example=350.0)
    category: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    date: str
    description: str
    amount: float
    category: str
    predicted_category: Optional[str]
    confidence: float
    created_at: str

class InsightResponse(BaseModel):
    total_spent: float
    top_category: str
    insights: List[str]
    category_breakdown: dict
    month_over_month: dict

class PredictionResponse(BaseModel):
    next_month_total: float
    by_category: dict
    confidence: str
    trend: str

class AdvisorRequest(BaseModel):
    question: str = Field(..., example="How can I reduce my food expenses?")

class AdvisorResponse(BaseModel):
    answer: str
    relevant_data: dict
    tips: List[str]

class CSVUploadResponse(BaseModel):
    imported: int
    failed: int
    transactions: List[dict]
