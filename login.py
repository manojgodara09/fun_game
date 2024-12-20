from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import psycopg2

# Configuration
SECRET_KEY = "d6A9bE3cAf2D6E5d8eFb6d8A6Bc9D1d5F7A2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL = "postgres://koyeb-adm:MK59GFoIzBZb@ep-shy-frost-a12m58cj.ap-southeast-1.pg.koyeb.app/koyebdb"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    balance: float

# Utility Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username(username: str):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, balance, logged_in FROM user_data WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def set_user_logged_in(username: str, logged_in: bool):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("UPDATE user_data SET logged_in=%s WHERE username=%s", (logged_in, username))
    conn.commit()
    conn.close()

# Login Endpoint
@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    user = get_user_by_username(request.username)
    if not user or not verify_password(request.password, user[1]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user[3]:  # Check if the user is already logged in
        raise HTTPException(status_code=403, detail="User already logged in")

    set_user_logged_in(request.username, True)  # Set user as logged in

    access_token = create_access_token(
        data={"sub": user[0]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "balance": user[2]}
