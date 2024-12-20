from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
DATABASE_URL = os.getenv("DATABASE_URL")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request Model
class LoginRequest(BaseModel):
    username: str
    password: str

# Response Model
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    balance: float

# Function to authenticate user
def authenticate_user(username: str, password: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM user_data WHERE username=%s", (username,))
        result = cursor.fetchone()
        conn.close()
        if result and pwd_context.verify(password, result[0]):
            return True
        return False
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to set user logged in status
def set_user_logged_in(username: str, logged_in: bool):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("UPDATE user_data SET logged_in=%s WHERE username=%s", (logged_in, username))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error setting user logged in status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Login Endpoint
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    try:
        logger.info(f"Attempting to authenticate user: {request.username}")
        if not authenticate_user(request.username, request.password):
            logger.warning(f"Authentication failed for user: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        logger.info(f"Setting user {request.username} as logged in")
        set_user_logged_in(request.username, True)  # Set user as logged in

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": request.username}, expires_delta=access_token_expires
        )
        
        # Fetch user balance
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM user_data WHERE username=%s", (request.username,))
        user_balance = cursor.fetchone()[0]
        conn.close()

        logger.info(f"User {request.username} logged in successfully")
        return {"access_token": access_token, "token_type": "bearer", "balance": user_balance}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
