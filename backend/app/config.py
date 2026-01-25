import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/taskforge",
)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
FRONTEND_URLS = [
    url.strip()
    for url in os.getenv("FRONTEND_URLS", FRONTEND_URL).split(",")
    if url.strip()
]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
REMEMBER_ME_REFRESH_DAYS = int(os.getenv("REMEMBER_ME_REFRESH_DAYS", "30"))
LOGIN_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("LOGIN_RATE_LIMIT_WINDOW_SECONDS", "60"))
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv("LOGIN_RATE_LIMIT_MAX_ATTEMPTS", "5"))
LOGIN_LOCKOUT_THRESHOLD = int(os.getenv("LOGIN_LOCKOUT_THRESHOLD", "5"))
LOGIN_LOCKOUT_MINUTES = int(os.getenv("LOGIN_LOCKOUT_MINUTES", "15"))
