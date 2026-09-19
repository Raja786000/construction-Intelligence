from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    name: str
    email: str
    role: str
    token: str

@router.post("/login")
def login(request: LoginRequest):
    # Accept admin or standard team credentials for easy demoing
    u = request.username.strip().lower()
    p = request.password.strip()

    if not u or not p:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    # Determine role and display name
    if "admin" in u:
        role = "System Administrator"
        name = "Site Admin"
        email = "admin@construction.ai"
    elif "safety" in u:
        role = "Safety Director"
        name = "Amina Said (CSP)"
        email = "safety@construction.ai"
    elif "manager" in u or "pm" in u:
        role = "Project Manager"
        name = "Rajesh Verma"
        email = "pm@construction.ai"
    else:
        role = "Site Engineer"
        name = request.username.split("@")[0].capitalize() or "Site Engineer"
        email = f"{u}@construction.ai" if "@" not in u else u

    token = f"token_ci_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {
        "success": True,
        "token": token,
        "user": {
            "username": request.username,
            "name": name,
            "email": email,
            "role": role
        }
    }

@router.get("/me")
def get_current_user():
    return {
        "authenticated": True,
        "user": {
            "username": "admin@construction.ai",
            "name": "Site Admin",
            "role": "System Administrator",
            "email": "admin@construction.ai"
        }
    }
