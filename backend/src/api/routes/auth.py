from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from src.core.database import get_db
from src.core.models import User
from src.core.schemas import RegisterRequest, RegisterResponse, ConfirmResponse
from src.core.mailer import send_confirmation_email, generate_token

router = APIRouter(tags=["auth"], prefix="/auth")

@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    token = generate_token()
    if existing:
        existing.is_confirmed = False
        existing.confirmation_token = token
        db.commit()
        try:
            send_confirmation_email(existing.email, token)
        except Exception:
            pass
        return RegisterResponse(id=existing.id, email=existing.email, is_confirmed=existing.is_confirmed)
    user = User(email=req.email, confirmation_token=token)
    db.add(user)
    db.commit()
    db.refresh(user)
    try:
        send_confirmation_email(user.email, token)
    except Exception:
        pass
    return RegisterResponse(id=user.id, email=user.email, is_confirmed=user.is_confirmed)

@router.get("/confirm", response_model=ConfirmResponse)
def confirm(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.confirmation_token == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Token invalide")
    user.is_confirmed = True
    user.confirmation_token = None
    db.commit()
    return ConfirmResponse(message="Email confirmé")
