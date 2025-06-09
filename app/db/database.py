from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

from dotenv import load_dotenv
import os
load_dotenv()

Database_Url=os.getenv("DATABASE_URI")
print("Database_Url:",Database_Url)

if not  Database_Url:
    raise ValueError("invalid database url")

engine= create_engine(Database_Url,echo=True,pool_size=10)

Base=declarative_base()
SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)
