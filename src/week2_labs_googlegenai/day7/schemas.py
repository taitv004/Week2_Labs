from pydantic import BaseModel, Field, model_validator
from typing import List

class LineItem(BaseModel):
    sku: str = Field(description="The product SKU or item code")
    quantity: int = Field(description="Quantity ordered")
    unit_price: float = Field(description="Price per single unit")

class Order(BaseModel):
    customer: str = Field(description="Name of the customer or company")
    items: List[LineItem] = Field(description="List of purchased line items")
    total_amount: float = Field(description="Subtotal cost of the order")
    requested_delivery_date: str = Field(description="Delivery date if specified")

    @model_validator(mode='after')
    def verify_totals(self) -> 'Order':
        """Reconciles that item quantities * unit prices match the total amount."""
        calculated_total = sum(item.quantity * item.unit_price for item in self.items)
        # Allow a tiny tolerance for floating-point rounding if needed, or strict equality
        if abs(calculated_total - self.total_amount) > 0.05:
            raise ValueError(f"Line items total ({calculated_total}) does not match stated total ({self.total_amount})")
        return self