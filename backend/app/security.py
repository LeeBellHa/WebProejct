"""
비밀번호를 평문으로 저장하고 비교하기 위한 모듈
"""
def get_password_hash(password: str) -> str:
    # 해싱 없이 그대로 반환
    return password

def verify_password(plain_password: str, stored_password: str) -> bool:
    # 평문 비교
    return plain_password == stored_password
