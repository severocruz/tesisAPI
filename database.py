from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cambia usuario, password, host, puerto y base de datos
DATABASE_URL = "mysql+pymysql://root:12345@localhost:3306/db_autoctono"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


