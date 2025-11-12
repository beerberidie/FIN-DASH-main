"""Category models."""

from pydantic import BaseModel, Field, field_validator

from utils.validation import validate_group


class CategoryBase(BaseModel):
    """Base category model."""

    name: str = Field(..., min_length=1, max_length=100)
    group: str  # 'needs', 'wants', 'savings', 'debt', 'income'
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str = Field(default="Circle", max_length=50)
    is_system: bool = False

    @field_validator("group")
    @classmethod
    def validate_group_value(cls, v):
        validate_group(v)
        return v


class CategoryCreate(CategoryBase):
    """Model for creating a category."""

    pass


class Category(CategoryBase):
    """Full category model with ID and timestamp."""

    id: str
    created_at: str

    @classmethod
    def from_csv(cls, row: dict) -> "Category":
        """Create Category from CSV row."""
        # Convert string 'true'/'false' to boolean
        row_copy = row.copy()
        row_copy["is_system"] = row_copy.get("is_system", "false").lower() == "true"
        return cls(**row_copy)

    def to_csv(self) -> dict:
        """Convert Category to CSV row."""
        data = self.model_dump()
        # Convert boolean to string for CSV
        data["is_system"] = "true" if data["is_system"] else "false"
        return data

    class Config:
        from_attributes = True


# Field names for CSV
CATEGORY_FIELDNAMES = [
    "id",
    "name",
    "group",
    "color",
    "icon",
    "is_system",
    "created_at",
]
