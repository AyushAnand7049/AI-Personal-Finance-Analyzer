from fastapi import APIRouter
from services.predictor import predict_next_month

router = APIRouter()

@router.get("/")
def get_prediction():
    """Predict next month's expenses using linear regression"""
    return predict_next_month()
