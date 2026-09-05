from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    department_id: int
    salary: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    bonus: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    hire_date: date | None = None


class EmployeeResponse(EmployeeCreate):
    employee_id: int

    model_config = {
        "from_attributes": True
    }