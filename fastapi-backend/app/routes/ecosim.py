from fastapi import APIRouter, status

from app.services.example_service import list_items, create_item
from app.schemas.ecosim import GetHouse, PostHouse
from app.services.ecosim import get_municipality_data
router = APIRouter()


@router.get("/", response_model=GetHouse)
async def get_ecosim_results():
    
    
    return {"What the sigmam": "ok"}


@router.post("/", response_model=PostHouse, status_code=status.HTTP_201_CREATED)
async def post_item(municipality: PostHouse, electricity_rate: float, 
                    current_electricity_bill: float, desired_savings: float):
    municipality_data = get_municipality_data(PostHouse.municipality)
    return {
                "municipality_data": municipality_data
                
            }
