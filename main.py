import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
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