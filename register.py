from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
import sqlite3

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

# Models
class RegisterRequest(BaseModel):
    username: str
    password: str
    balance: float
    access_pass: str  # Admin security key

class BalanceUpdateRequest(BaseModel):
    username: str
    new_balance: float
    access_pass: str  # Admin security key

# Security Configuration
ADMIN_PASS = "admin_secret_pass"  # Replace with a secure passphrase

# Utility Functions
def add_user_to_database(username: str, hashed_password: str, balance: float):
    conn = sqlite3.connect("casino.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user_data (username, password, balance) VALUES (?, ?, ?)",
                       (username, hashed_password, balance))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

def update_user_balance(username: str, new_balance: float):
    conn = sqlite3.connect("casino.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE user_data SET balance=? WHERE username=?", (new_balance, username))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()
    conn.close()

# Register Endpoint (Admin Access)
@router.post("/register")
def register_user(request: RegisterRequest):
    if request.access_pass != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    hashed_password = pwd_context.hash(request.password)
    add_user_to_database(request.username, hashed_password, request.balance)
    return {"message": f"User '{request.username}' created successfully"}

# Balance Update Endpoint (Admin Access)
@router.post("/update_balance")
def update_balance(request: BalanceUpdateRequest):
    if request.access_pass != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    update_user_balance(request.username, request.new_balance)
    return {"message": f"Balance for user '{request.username}' updated to {request.new_balance}"}
