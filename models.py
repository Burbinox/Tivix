from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, JSON


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(Integer, ForeignKey("users.id"))
    income = Column(JSON)
    outcome = Column(JSON)


class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)
    budget = Column(Integer, ForeignKey("budgets.id"))
    user = Column(Integer, ForeignKey("users.id"))
