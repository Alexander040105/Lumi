from fastapi import APIRouter, status
from app.schemas.ecosim import EcosimResponse, GetHouse, PostHouse
from app.services.ecosim import get_municipality_data, renewable_energy_calculator, consumption_calculator
router = APIRouter()


@router.get("/", response_model=GetHouse)
async def get_ecosim_results():
    return {"What the sigmam": "ok"}


@router.post("/", response_model=EcosimResponse, status_code=status.HTTP_201_CREATED)
async def post_item(body: PostHouse):
    municipality_data = get_municipality_data(body.municipality)
    consumption_results = consumption_calculator(
        body.current_electricity_bill,
        body.electricity_rate,
        body.desired_savings,
    )
    renewable_energy_results = renewable_energy_calculator(
        body.municipality,
        body.current_electricity_bill,
        body.electricity_rate,
        body.desired_savings,
    )
    return {
        "municipality_data": municipality_data,
        "consumption_results": consumption_results,
        "renewable_energy_results": renewable_energy_results,
    }
