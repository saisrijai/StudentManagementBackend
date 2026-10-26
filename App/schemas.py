```python
from datetime import date
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class StudentBase(BaseModel):
    name: str
    date_of_birth: date
    email: EmailStr
    phone: str
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None


class StudentResponse(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
```
