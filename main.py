from fastapi import FastAPI, Depends, Request, Response, status
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from utils import hash_password, create_session_token

app = FastAPI()
app.SECRETKET = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def root(request: Request):
    return HTMLResponse("""<h1>This is Family budget app</h1>
    <p>For doumentation go to <a href="/docs">Docks</a></p> 
    """)


@app.post("/register")
def create_user(username: str, password: str, response: Response,  db: Session = Depends(get_db)):
    check_if_user_already_exist = db.query(models.User).filter(models.User.username == username).first()
    if check_if_user_already_exist:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"User already exist, try again"}

    hassed_password = hash_password(password, app.SECRETKET)
    session_token = create_session_token(app.SECRETKET)
    db_user = models.User(username=username, password=hassed_password, session_id=session_token)
    db.add(db_user)
    db.commit()
    response.status_code = status.HTTP_201_CREATED
    return "User created!"


@app.post("/login")
def login(username: str, password: str, response: Response,  db: Session = Depends(get_db)):
    check_if_user_already_exist = db.query(models.User).filter(models.User.username == username).first()
    hassed_password = hash_password(password, app.SECRETKET)
    check_if_password_correct = db.query(models.User).filter(models.User.password == hassed_password).first()
    if check_if_user_already_exist and check_if_password_correct:
        response.set_cookie(key="session_token", value=check_if_user_already_exist.session_id)
        response.status_code = status.HTTP_202_ACCEPTED

