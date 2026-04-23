from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..database import get_db
from ..models import Category, Product
from ..schemas import CategoryStats, ProductCreate, ProductOut

router = APIRouter(prefix="/api", tags=["catalog"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


# Endpoint 1: List all products (async, JOIN via joinedload)
@router.get("/products/", response_model=list[ProductOut])
async def product_list(db: DbDep) -> list[ProductOut]:
    """
    List products with category JOIN.
    FastAPI: async SQLAlchemy query with joinedload (no N+1).
    Django equivalent: Product.objects.select_related('category').all()
    """
    result = await db.execute(
        select(Product).options(joinedload(Product.category)).order_by(Product.id.desc())
    )
    products = result.scalars().unique().all()
    return [_to_product_out(p) for p in products]


# Endpoint 2: Get product by ID
@router.get("/products/{product_id}/", response_model=ProductOut)
async def product_detail(product_id: int, db: DbDep) -> ProductOut:
    result = await db.execute(
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return _to_product_out(product)


# Endpoint 3: Create product
@router.post("/products/create/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def product_create(payload: ProductCreate, db: DbDep) -> ProductOut:
    # Verify category exists
    category = await db.get(Category, payload.category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"category_id": ["Invalid pk — object does not exist."]},
        )
    product = Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    # Load category for response
    await db.refresh(product, ["category"])
    return _to_product_out(product)


# Endpoint 4: Update product
@router.put("/products/{product_id}/update/", response_model=ProductOut)
async def product_update(product_id: int, payload: ProductCreate, db: DbDep) -> ProductOut:
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    category = await db.get(Category, payload.category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"category_id": ["Invalid pk — object does not exist."]},
        )
    for field, value in payload.model_dump().items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    await db.refresh(product, ["category"])
    return _to_product_out(product)


# Endpoint 5: Categories with product count (async aggregation)
@router.get("/categories/stats/", response_model=list[CategoryStats])
async def categories_with_product_count(db: DbDep) -> list[CategoryStats]:
    """
    Complex aggregation query.
    FastAPI: SQLAlchemy func.count() with group_by — runs async.
    Django equivalent: Category.objects.annotate(product_count=Count('products'))

    Key migration difference: SQLAlchemy returns tuples from aggregate queries,
    not ORM objects. We map them manually to Pydantic schemas.
    """
    result = await db.execute(
        select(
            Category.id,
            Category.name,
            Category.slug,
            func.count(Product.id).label("product_count"),
        )
        .join(Product, Product.category_id == Category.id, isouter=True)
        .group_by(Category.id)
        .order_by(Category.name)
    )
    rows = result.all()
    return [
        CategoryStats(id=row.id, name=row.name, slug=row.slug, product_count=row.product_count)
        for row in rows
    ]


def _to_product_out(product: Product) -> ProductOut:
    return ProductOut(
        id=product.id,
        name=product.name,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id,
        category_name=product.category.name,
        created_at=product.created_at,
    )
