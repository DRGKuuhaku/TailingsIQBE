from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import os
import json
from routers import query_assistant, risk_assessment, monitoring, knowledge_management

# Create FastAPI app
app = FastAPI(title="TailingsIQ API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query_assistant.router)
app.include_router(risk_assessment.router)
app.include_router(monitoring.router)
app.include_router(knowledge_management.router)

# Authentication models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Mock user database
fake_users_db = {
    "test_user": {
        "username": "test_user",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "password",  # In production, use proper password hashing
        "disabled": False,
    }
}

# JWT settings
SECRET_KEY = "your-secret-key"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authentication functions
def verify_password(plain_password, hashed_password):
    # In production, use proper password verification
    return plain_password == hashed_password

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
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

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to TailingsIQ API",
        "version": "1.0.0",
        "documentation": "/docs",
        "modules": [
            "Query Assistant",
            "Risk Assessment",
            "Monitoring",
            "Knowledge Management"
        ]
    }

# Sample data endpoints
@app.get("/api/facilities")
async def get_facilities(current_user: User = Depends(get_current_active_user)):
    """Get list of all facilities"""
    facilities = [
        {"id": "FAC001", "name": "North Basin Facility", "location": "Northern Region", "status": "Active"},
        {"id": "FAC002", "name": "South Basin Facility", "location": "Southern Region", "status": "Active"},
        {"id": "FAC003", "name": "East Basin Facility", "location": "Eastern Region", "status": "Maintenance"},
        {"id": "FAC004", "name": "West Basin Facility", "location": "Western Region", "status": "Active"}
    ]
    return facilities

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
