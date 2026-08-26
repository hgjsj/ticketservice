from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, engine, ensure_user_profile_columns, get_db
from app.security import JWT_EXPIRE_MINUTES, create_access_token

Base.metadata.create_all(bind=engine)
ensure_user_profile_columns()

app = FastAPI(title="Auth Service API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register", response_model=schemas.UserRead)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, payload)


@app.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, payload.username)
    if not user or user.hashed_password != f"plain::{payload.password}":
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return schemas.TokenResponse(access_token=create_access_token(user), expires_in=JWT_EXPIRE_MINUTES * 60)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth"}