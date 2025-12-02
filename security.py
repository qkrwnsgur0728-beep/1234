from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

# --- 설정 ---
SECRET_KEY = "your_secret_key_keep_it_safe"  # 암호화 키 (임의로 변경 가능)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 토큰 만료 시간 (24시간)

# 비밀번호 해싱 도구 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash:
    @staticmethod
    def bcrypt(password: str):
        """비밀번호를 암호화(해싱)합니다."""
        return pwd_context.hash(password)

    @staticmethod
    def verify(plain_password, hashed_password):
        """입력된 비밀번호가 암호화된 비밀번호와 일치하는지 확인합니다."""
        return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """JWT 액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """토큰의 유효성을 검사합니다."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception