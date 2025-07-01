# backend/app/schemas/user.py
from typing import Optional, Literal
from pydantic import BaseModel, constr

class UserCreate(BaseModel):
    login_id:   constr(min_length=2, max_length=50)
    password:   constr(min_length=8)
    username:   constr(min_length=1, max_length=100)   # 실명
    student_id: constr(min_length=5, max_length=20)
    major:      constr(min_length=1, max_length=100)
    phone:      Optional[constr(min_length=9, max_length=20)] = None

class UserRead(BaseModel):
    id:         int
    login_id:   str
    username:   str
    student_id: str
    major:      str
    phone:      Optional[str]
    role:       Literal["pending", "user", "admin"]     # role: 회원가입 완료 일반유저 | 가입대기 | 관리자

    class Config:
        orm_mode = True
