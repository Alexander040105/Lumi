from uuid import uuid4

from app.schemas.example import ItemCreate, ItemOut

_ITEMS: list[ItemOut] = []


async def list_items() -> list[ItemOut]:
    return _ITEMS


async def create_item(payload: ItemCreate) -> ItemOut:
    item = ItemOut(id=str(uuid4()), name=payload.name, description=payload.description)
    _ITEMS.append(item)
    return item
