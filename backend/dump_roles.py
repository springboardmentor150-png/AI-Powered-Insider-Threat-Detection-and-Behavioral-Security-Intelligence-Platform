import os
from sqlalchemy import create_engine
from app.models import User
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
session = Session()
users = session.query(User).all()
for u in users:
    print(u.email, getattr(u, 'role', 'NO_ROLE'))
