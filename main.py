from fastapi import APIRouter, Depends, HTTPException, Request, status, Response, FastAPI
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import base64
import os 

# models.py에서 정의한 클래스들 import
from models import User, Role, Product, Measurement, get_db, Base, engine 
from security import Hash, create_access_token, verify_token

# ★★★ [핵심] 서버 시작 시 DB 테이블이 없으면 자동으로 생성 ★★★
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# API 주소 프리픽스
router = APIRouter(prefix="/api", tags=["Auth & System"])

# --- 데이터 규격 (Schemas) ---
class UserSignup(BaseModel):
    id: str
    pw: str
    name: str

class UserLogin(BaseModel):
    id: str
    pw: str

class LogRequest(BaseModel):
    startDate: str

class LogResponse(BaseModel):
    mid: int
    timestamp: str  
    product_name: str
    result: str     # Pydantic은 여기에 str이 오기를 기대함

class ImageResponse(BaseModel):
    img1_base64: Optional[str] = None
    img2_base64: Optional[str] = None

# --- [1] 회원가입 ---
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(request: UserSignup, db: Session = Depends(get_db)):
    if db.query(User).filter(User.id == request.id).first():
        raise HTTPException(status_code=401, detail="이미 존재하는 ID입니다.")
    
    if db.query(Role).count() == 0:
        db.add(Role(role_name="admin"))
        db.add(Role(role_name="staff"))
        db.commit()

    new_user = User(
        id=request.id,
        pw=Hash.bcrypt(request.pw),
        name=request.name,
        role_id=2 
    )
    db.add(new_user)
    db.commit()
    
    return {"status": "success", "message": "회원가입 완료"}

# --- (중략: 로그인, 로그아웃, 상태확인 API) ---

# --- [5] 로그 리스트 조회 (WPF 연동용) ---
@router.post("/logs", response_model=List[LogResponse])
def get_logs(req: LogRequest, db: Session = Depends(get_db)):
    logs = db.query(Measurement).join(Product)\
             .filter(Measurement.measured_at.like(f"{req.startDate}%"))\
             .order_by(Measurement.MID.desc())\
             .all()

    results = []
    for log in logs:
        p_name = log.product.product_name if log.product else "Unknown"
        results.append(LogResponse(
            mid=log.MID,
            timestamp=log.measured_at, 
            product_name=p_name,
            # ⚠️ 최종 수정 8: log.inspection_result가 None이면 빈 문자열 ""로 대체하여 Pydantic 에러 방지
            result=log.inspection_result if log.inspection_result else ""
        ))
    return results

# --- [6] 이미지 상세 조회 (WPF 연동용) ---
@router.get("/logs/{mid}/images", response_model=ImageResponse)
def get_log_images(mid: int, db: Session = Depends(get_db)):
    log = db.query(Measurement).filter(Measurement.MID == mid).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    def encode_img_from_path(path_str):
        """파일 경로에서 이미지를 읽어 Base64 문자열로 인코딩합니다."""
        if not path_str or not os.path.exists(path_str):
            return None
        
        try:
            with open(path_str, "rb") as f:
                img_data = f.read()
            return base64.b64encode(img_data).decode('utf-8')
        except Exception:
            return None 

    return ImageResponse(
        img1_base64=encode_img_from_path(log.cam1_path),
        img2_base64=encode_img_from_path(log.cam2_path)
    )

# --- (이하 나머지 API 함수 생략) ---

app.include_router(router)