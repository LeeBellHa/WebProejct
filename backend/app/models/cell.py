from sqlalchemy import Column, Integer
from app.database import Base

class Cell(Base):
    __tablename__ = "cells"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    floor = Column(Integer, index=True, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
