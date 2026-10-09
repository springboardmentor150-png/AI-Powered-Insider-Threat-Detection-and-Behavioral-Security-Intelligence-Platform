from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from app.models import User
from dotenv import load_dotenv
load_dotenv()
session = sessionmaker(bind=create_engine(os.getenv('DATABASE_URL')))()
for u in session.query(User).all():
    print(f"{u.email} -> {u.role}")
