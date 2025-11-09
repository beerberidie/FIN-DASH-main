"""Category API endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException

from models.category import Category, CategoryCreate, CATEGORY_FIELDNAMES
from services.csv_manager import csv_manager
from utils.ids import generate_category_id
from utils.dates import now_iso

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[Category])
def list_categories():
    """List all categories."""
    categories = csv_manager.read_csv("categories.csv")
    return [Category.from_csv(cat) for cat in categories]


@router.get("/{category_id}", response_model=Category)
def get_category(category_id: str):
    """Get a single category by ID."""
    categories = csv_manager.read_csv("categories.csv")
    
    for cat_data in categories:
        if cat_data.get('id') == category_id:
            return Category.from_csv(cat_data)
    
    raise HTTPException(status_code=404, detail="Category not found")


@router.post("", response_model=Category, status_code=201)
def create_category(category: CategoryCreate):
    """Create a new custom category."""
    # Generate ID and timestamp
    cat_id = generate_category_id(category.group, category.name)
    timestamp = now_iso()
    
    # Check if category already exists
    categories = csv_manager.read_csv("categories.csv")
    for cat in categories:
        if cat.get('id') == cat_id:
            raise HTTPException(status_code=400, detail="Category already exists")
    
    # Create category object
    cat_data = category.model_dump()
    cat_data['id'] = cat_id
    cat_data['created_at'] = timestamp
    
    # Convert to CSV format
    cat_obj = Category(**cat_data)
    
    # Append to CSV
    csv_manager.append_csv("categories.csv", cat_obj.to_csv(), CATEGORY_FIELDNAMES)
    
    return cat_obj


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: str):
    """Delete a custom category (system categories cannot be deleted)."""
    categories = csv_manager.read_csv("categories.csv")
    
    # Find category and check if it's a system category
    for cat in categories:
        if cat.get('id') == category_id:
            if cat.get('is_system', 'false').lower() == 'true':
                raise HTTPException(status_code=400, detail="Cannot delete system category")
            break
    
    success = csv_manager.delete_csv_row(
        "categories.csv",
        category_id,
        CATEGORY_FIELDNAMES
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return None

