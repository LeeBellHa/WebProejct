# backend/app/schemas/user.py
from typing import Optional, Literal
from pydantic import BaseModel, constr

class UserCreate(BaseModel):
    login_id:   constr(min_length=2, max_length=50) #아이디
    password:   constr(min_length=8) # 비밀번호
    username:   constr(min_length=1, max_length=100)   # 실명
    student_id: constr(min_length=7, max_length=9) # 학번
    major:      constr(min_length=1, max_length=100) # 학과 (일단은 string으로, 나중에 enum으로)
    phone:      Optional[constr(min_length=9, max_length=20)] = None # 전화번호

class UserRead(BaseModel):
    user_id:         int
    login_id:   str
    password: Optional[str] = None  
    username:   str
    student_id: str
    major:      str
    phone:      Optional[str]
    role:       Literal["pending", "user", "admin"]     # role: 회원가입 완료  가입대기 | 일반유저 | 관리자

    class Config:
        orm_mode = True
