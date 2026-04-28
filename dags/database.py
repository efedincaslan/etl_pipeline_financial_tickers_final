from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
db_user = os.getenv('connection_string')
engine = create_engine(db_user)