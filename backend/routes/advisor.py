from fastapi import APIRouter
from models.schemas import AdvisorRequest, AdvisorResponse
from services.advisor import get_advisor_response

router = APIRouter()

@router.post("/")
async def ask_advisor(request: AdvisorRequest):
    """Ask the AI financial advisor a question"""
    result = await get_advisor_response(request.question)
    return result
