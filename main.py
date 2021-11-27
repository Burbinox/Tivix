from fastapi import FastAPI, Depends
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/register")
def create_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = models.User(username=username, password=password)
    db.add(db_user)
    db.commit()
    return "User created!"
