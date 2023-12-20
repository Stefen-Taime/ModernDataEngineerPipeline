from fastapi import APIRouter, Depends, HTTPException, status, Request
from models.models import User, UserCreate, Token
from utils.utils import get_password_hash, create_access_token, verify_password
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))

router = APIRouter()

async def get_admin_db(request: Request):
    return request.app.token_user_db

async def authenticate_user(db, username: str, password: str):
    user = await db["users"].find_one({"username": username})
    if user:
        if verify_password(password, user["password"]):
            return user
    return None

# Routes
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorClient = Depends(get_admin_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=User)
async def create_user(user: UserCreate, request: Request):
    db = request.app.token_user_db 
    collection = db["users"]
    hashed_password = get_password_hash(user.password)
    db_user = {"username": user.username, "password": hashed_password}
    user_id = await collection.insert_one(db_user)  
    new_user = await collection.find_one({"_id": user_id.inserted_id})
    new_user["id"] = str(new_user["_id"])
    del new_user["_id"]
    return new_user
