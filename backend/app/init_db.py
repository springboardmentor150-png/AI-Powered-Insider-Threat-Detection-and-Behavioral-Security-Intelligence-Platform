from .database import Base, engine
from . import models

Base.metadata.create_all(bind=engine)

print("Database tables created!")