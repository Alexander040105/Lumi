from fastapi import APIRouter, Query

from app.schemas.products import (
    ProductRecommendationRequest,
    ProductRecommendationResponse,
    ProductBrowseResponse,
    ProductAuditResponse,
)
from app.services.products import (
    get_product_recommendations,
    browse_products,
    get_product_data_audit,
)

router = APIRouter()


@router.get("/recommend", response_model=ProductRecommendationResponse)
async def recommend_products(
    energy_type: str = Query(..., description="Renewable type: solar, wind, hydro, geothermal"),
    budget_php: float | None = Query(default=None, description="Optional budget ceiling in PHP"),
    limit: int = Query(default=5, ge=1, le=20),
):
    """Get context-aware product recommendations for a renewable energy type.

    Returns actual scraped products from Alibaba, Amazon, Lazada, and Shopee.
    Links are not fabricated; products without URLs are excluded.
    """
    return get_product_recommendations(energy_type, budget_php=budget_php, limit=limit)


@router.get("/browse", response_model=ProductBrowseResponse)
async def browse_products_endpoint(
    category: str | None = Query(default=None),
    subcategory: str | None = Query(default=None),
    source_site: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """Browse all scraped products with filters and pagination."""
    return browse_products(
        category=category,
        subcategory=subcategory,
        source_site=source_site,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size,
    )


@router.get("/audit", response_model=ProductAuditResponse)
async def product_audit():
    """Return a data quality audit of the scraped product dataset.

    Includes counts of missing URLs, misclassified categories, and
    recommendations for scraper improvements.
    """
    return get_product_data_audit()
