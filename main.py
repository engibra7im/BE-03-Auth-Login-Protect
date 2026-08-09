import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends, Response
from supabase import create_client, Client
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 8000))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment variables.")

supabase:Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

app = FastAPI()

class AuthRequest(BaseModel):
    email: str
    password: str

def get_current_user(
    authorization: str | None = Header(default=None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    try:
        response = supabase.auth.get_user(token)
        user = response.user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user

@app.get("/")
def root():
    return{
        "name": "Auth API",
        "Status": "Server running and connected to Supabase successfully",
    }

@app.post("/auth/signup", status_code=201)
def signup(data: AuthRequest):
    if not data.email.strip() or not data.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        return {
            "user": response.user
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.post("/auth/login")
def login(data: AuthRequest):
    if not data.email.strip() or not data.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This is a public endpoint."
    }

@app.get("/protected/profile")
def protected_profile(
    user = Depends(get_current_user)
):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }

@app.post("/auth/logout", status_code=204)
def logout(user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return Response(status_code=204)

@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)):
    return {
        "message": "Welcome to your dashboard!",
        "user_id": user.id,
        "email": user.email
    }