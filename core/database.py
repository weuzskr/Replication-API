import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_A_URL = os.getenv("DB_A_URL", "postgresql://postgres:1234@localhost:5432/replica_a")
DB_B_URL = os.getenv("DB_B_URL", "postgresql://postgres:1234@localhost:5432/replica_b")

engine_a = create_engine(DB_A_URL)
engine_b = create_engine(DB_B_URL)

SessionA = sessionmaker(bind=engine_a)
SessionB = sessionmaker(bind=engine_b)
