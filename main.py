from fastapi import FastAPI, Depends, Request, Response, status
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from utils import hash_password, create_session_token
from pydantic import BaseModel

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
def registration(username: str, password: str, response: Response,  db: Session = Depends(get_db)):
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
    return {"User created! You can login now"}


@app.post("/login")
def login(username: str, password: str, response: Response,  db: Session = Depends(get_db)):
    exising_user = db.query(models.User).filter(models.User.username == username).first()
    hassed_password = hash_password(password, app.SECRETKET)
    check_if_password_correct = db.query(models.User).filter(models.User.password == hassed_password).first()
    if exising_user and check_if_password_correct:
        response.set_cookie(key="session_token", value=exising_user.session_id)
        response.status_code = status.HTTP_202_ACCEPTED
        return {"Login Sucess"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Invalid username or password"}


@app.get("/budgets")
def get_budgets(request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.session_id == request.cookies.get("session_token")).first()
    if user:
        budgets = db.query(models.Budget).filter(models.Budget.owner == user.id).all()
        print(budgets)
        return budgets
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"Unauthorized user"}


class Budget(BaseModel):
    income: dict
    outcome: dict


@app.post("/budget/{budget_id}")
async def post_budgets(budget_id, budget: Budget, request: Request, response: Response, db: Session = Depends(get_db)):
    authorized_user = db.query(models.User).filter(models.User.session_id == request.cookies.get("session_token")).first()
    exist_budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    owner = db.query(models.Budget).filter(models.Budget.owner == authorized_user.id).first()
    if authorized_user:
        if exist_budget:
            if owner:
                exist_budget.income = budget.income
                exist_budget.outcome = budget.outcome
                response.status_code = status.HTTP_200_OK
                return {"Updated budget number: " + budget_id}
            else:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {"You are not the owner of this budget"}
        else:
            db_budget = models.Budget(id=budget_id, owner=authorized_user.id, income=budget.income,
                                      outcome=budget.outcome)
            db.add(db_budget)
            db.commit()
            response.status_code = status.HTTP_201_CREATED
            return {"Created budget number: " + budget_id}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"Unauthorized user"}

