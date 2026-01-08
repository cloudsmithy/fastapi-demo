from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    message: str = ""


@router.post("/submit")
def submit_form(form: ContactForm):
    return {
        "name": form.name,
        "email": form.email,
        "age": form.age,
        "message": form.message,
    }
