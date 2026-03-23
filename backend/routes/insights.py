from fastapi import APIRouter
from services.insights_engine import generate_insights

router = APIRouter()

@router.get("/")
def get_insights():
    """Get AI-generated spending insights"""
    return generate_insights()
