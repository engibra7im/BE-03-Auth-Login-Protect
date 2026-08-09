import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client

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

@app.get("/")
def root():
    return{
        "name": "Auth API",
        "Status": "Server running and connected to Supabase successfully",
    }