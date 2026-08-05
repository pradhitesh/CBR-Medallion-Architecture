import os
from dotenv import load_dotenv

# The environment variables are loaded from the .env file
# To be used by alembic, delembic, src folders
load_dotenv(os.path.join(os.path.dirname(__file__), "secrets.env"))