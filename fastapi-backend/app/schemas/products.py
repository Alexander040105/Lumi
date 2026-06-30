from pydantic import BaseModel, Field
from typing import Any


class ProductItem(BaseModel):
    product_name: str | None = None
    price_value: float | None = None
    currency: str | None = None
    energy_category: str | None = None
    energy_subcategory: str | None = None
    source_site: str | None = None
    url: str | None = None
    ratings: str | None = None
    reviews: str | None = None


class ProductRecommendationRequest(BaseModel):
    energy_type: str = Field(..., description="solar, wind, hydro, or geothermal")
    budget_php: float | None = Field(default=None, ge=0)


class ProductRecommendationResponse(BaseModel):
    energy_type: str
    items: list[ProductItem]
    count: int
    note: str = ""


class ProductBrowseResponse(BaseModel):
    items: list[ProductItem]
    total: int
    page: int
    page_size: int
    note: str = ""


class ProductAuditResponse(BaseModel):
    total_products: int
    with_url: int
    without_url: int
    hydro_misclassified_as_wind: int
    solar_misclassified: int
    category_counts: dict[str, int]
    source_counts: dict[str, int]
    recommendations: list[str]
