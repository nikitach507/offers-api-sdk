from uuid import UUID

from pydantic import BaseModel


class Offer(BaseModel):
    """
    Represents an offer for a product.

    Attributes:
        id (UUID): Unique identifier for the offer.
        price (int): Price of the offer in cents.
        items_in_stock (int): Number of items available in stock for this offer.
    """
    id: UUID
    price: int
    items_in_stock: int
