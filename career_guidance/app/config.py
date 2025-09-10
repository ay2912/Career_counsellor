import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database paths
DATABASE_URL = f"sqlite:///{DATA_DIR / 'career_guidance.db'}"
EXAMPLE_QUESTIONS_PATH = DATA_DIR / "example_questions.txt"

# Auth settings
SESSION_TIMEOUT = 3600  # 1 hour

# coursera api
COURSERA_API_KEY = "xIJxjyxG2Y1ND8Wx7ajZDtpa2Jozy3cOUVYyZJ9G2kLEEXhJ"
COURSERA_API_SECRET = "vn4b4w5M1G9fvfZDh1j90AEDGt3UhB1qdgsyFUHPhoySXMqvCIyHGXjG6PtxtdUC"