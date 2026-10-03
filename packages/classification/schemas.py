from pydantic import BaseModel, ConfigDict

from packages.tickets.enums import Category, Priority


class ClassificationResult(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)

    category: Category
    priority: Priority
    summary: str
