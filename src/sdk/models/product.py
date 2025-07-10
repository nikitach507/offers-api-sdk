from uuid import UUID

from pydantic import BaseModel


class Product(BaseModel):
    """
    Represents a product in the system.

    Attributes:
        id (UUID): Unique identifier for the product.
        name (str): Name of the product.
        description (str): Description of the product.
    """
    id: UUID | None = None
    name: str
    description: str
