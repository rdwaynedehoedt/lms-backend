from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..schemas.users import TokenData
from ..models.users import User, StudentProfile
from ..database.database import get_db

# Configuration
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # In production, use a secure key and store in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  # Updated to match the new token URL

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Function to check if user is lecturer
async def get_current_lecturer(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. You must be a lecturer to perform this action.",
        )
    return current_user

# Function to check if user is student and get their profile
async def get_current_student(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. You must be a student to perform this action.",
        )
    
    # Get the student profile
    student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile not found. Please complete your profile setup."
        )
    
    return current_user

# Function to check if user is admin
async def get_current_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. You must be an admin to perform this action.",
        )
    return current_user 