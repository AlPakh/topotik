from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("postgresql://topotik_test_db_user:tUNRiVqHiwDGIz2SyqhGcJQYIezYJZKz@dpg-cv4btiggph6c738ub4a0-a.frankfurt-postgres.render.com/topotik_test_db")  # Переменная для подключения к базе

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)
