from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# --- [1] 데이터베이스 연결 설정 ---

# 현재 파일 위치 기준 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "factory.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 세션 및 Base 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB 세션 의존성 함수 (FastAPI에서 Depends로 사용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- [2] 테이블 정의 ---

# 권한 테이블
class Role(Base):
    __tablename__ = "Role"
    RID = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String, nullable=False)
    users = relationship("User", back_populates="role")

# 사용자 테이블
class User(Base):
    __tablename__ = "User"
    UID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    id = Column(String, unique=True, index=True, nullable=False)
    pw = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("Role.RID"))
    role = relationship("Role", back_populates="users")

# [추가] 제품 테이블
class Product(Base):
    __tablename__ = "PRODUCT"
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    # ⚠️ 최종 수정 7: name -> product_name
    product_name = Column(String, nullable=False)

# [추가] 측정 기록 테이블
class Measurement(Base):
    __tablename__ = "MEASUREMENTS"
    MID = Column(Integer, primary_key=True, autoincrement=True)
    
    product_id = Column(Integer, ForeignKey("PRODUCT.product_id")) 
    measured_at = Column(String)
    inspection_result = Column(String, default="OK")
    cam1_path = Column(String)
    cam2_path = Column(String)

    # 관계 설정 (Join용)
    product = relationship("Product", foreign_keys=[product_id])