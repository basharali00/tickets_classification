from pydantic import BaseModel

from packages.tickets.enums import Category, Priority


class ClassificationResult(BaseModel):
    category: Category
    priority: Priority
    summary: str
