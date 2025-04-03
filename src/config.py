from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config(BaseModel):
    # Zendesk Configuration
    ZENDESK_API_URL: str = os.getenv("ZENDESK_API_URL", "https://aidl-001-zd-mock.replit.app")
    ZENDESK_API_KEY: str = os.getenv("ZENDESK_API_KEY", "")
    SUPPORT_USER_ID: int = int(os.getenv("SUPPORT_USER_ID", "111"))

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_HOST: str = os.getenv("OPENROUTER_API_HOST", "https://openrouter.ai/api/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemini-2.5-pro-exp-03-25:free")

    # Embedding Configuration
    EMBEDDINGS_MODEL: str = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")

    # Vector Store Configuration
    VECTOR_STORE_PATH: str = "./data/chroma"

config = Config() 