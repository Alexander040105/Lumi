from fastapi import APIRouter, status

from app.schemas.example import ItemCreate, ItemOut, ItemList
from app.services.example_service import list_items, create_item

router = APIRouter()


@router.get("/", response_model=ItemList)
async def get_items():
    items = await list_items()
    return {"items": items}


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def post_item(payload: ItemCreate):
    item = await create_item(payload)
    return item
