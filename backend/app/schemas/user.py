# backend/app/schemas/user.py

from typing import Optional, Literal
from pydantic import BaseModel, constr, Field

class UserCreate(BaseModel):
    login_id:   constr(min_length=2, max_length=50)
    password:   constr(min_length=8)
    username:   constr(min_length=1, max_length=100)
    student_id: constr(min_length=5, max_length=20)
    major:      Literal[
                    "뮤직테크놀러지&컴퓨터음악작곡",
                    "싱어송라이터전공",
                    "재즈퍼포먼스전공",
                ]
    phone:      Optional[str] = Field(
                   None,
                   pattern=r"^010-\d{4}-\d{4}$",
                   description="010-1234-5678 형식의 전화번호"
               )

class UserRead(BaseModel):
    id:         int
    login_id:   str
    username:   str
    student_id: str
    major:      Literal[
                    "뮤직테크놀러지&컴퓨터음악작곡",
                    "싱어송라이터전공",
                    "재즈퍼포먼스전공",
                ]
    phone:      Optional[str]
    role:       Literal["pending", "user", "admin"]

    class Config:
        orm_mode = True
