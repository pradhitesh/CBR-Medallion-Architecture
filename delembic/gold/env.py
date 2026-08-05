import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import create_engine
from config import *

# Read the DB URL directly from env to avoid configparser's `%`-interpolation
DB_URL = os.getenv('GOLD_PROD_URI')

def get_engine():
    return create_engine(DB_URL)
