from fastapi import APIRouter, status
from app.schemas.ecosim import EcosimResponse, GetHouse, PostHouse
from app.services.ecosim import get_municipality_data, renewable_energy_calculator, consumption_calculator
router = APIRouter()


@router.get("/", response_model=GetHouse)
async def get_ecosim_results():
    return {"What the sigmam": "ok"}


@router.post("/", response_model=EcosimResponse, status_code=status.HTTP_201_CREATED)
async def post_item(body: PostHouse):
    renewable_energy_results = renewable_energy_calculator(
        body.municipality,
        body.current_electricity_bill,
        body.electricity_rate,
        body.desired_savings,
    )
    return {
        "renewable_energy_results": renewable_energy_results,
    }
