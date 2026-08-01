from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemOut(BaseModel):
    id: str
    name: str
    description: str | None = None


class ItemList(BaseModel):
    items: list[ItemOut]
