from fastapi import FastAPI, Depends, Request, Response, status
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from utils import hash_password, create_session_token
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic_models import Budget, ShareBudget

app = FastAPI()
app.SECRETKET = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/app", response_class=HTMLResponse, include_in_schema=False)
def test(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/", include_in_schema=False)
async def root():
    return HTMLResponse("""<h1>This is Family budget app</h1>
    <p>For doumentation go to <a href="/docs">Docks</a></p>
    <p>or go to the <a href="/app">app</a> page</p>  
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


@app.get("/budget")
def get_budgets(request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.session_id == request.cookies.get("session_token")).first()
    if user:
        budgets = db.query(models.Budget).filter(models.Budget.owner == user.id).all()
        return budgets
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"Unauthorized user"}


@app.post("/budget/{budget_id}")
def post_budgets(budget_id, budget: Budget, request: Request, response: Response, db: Session = Depends(get_db)):
    authorized_user = db.query(models.User).filter(models.User.session_id == request.cookies.get("session_token")).first()
    exist_budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    owner = db.query(models.Budget).filter(models.Budget.owner == authorized_user.id).first()
    if authorized_user:
        if exist_budget:
            if owner:
                exist_budget.income = budget.income
                exist_budget.outcome = budget.outcome
                db.commit()
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


@app.get("/share")
def get_shares(request: Request, response: Response, db: Session = Depends(get_db)):
    authorized_user = db.query(models.User).filter(models.User.session_id == request.cookies.get("session_token")).first()
    if authorized_user:
        users_shares = db.query(models.Share).filter(models.Share.user == authorized_user.id).all()
        all_budgets = []
        for share in users_shares:
            all_budgets.append(db.get(models.Budget, share.budget))
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"Unauthorized user"}
    return all_budgets


@app.post("/share")
def share_budget(share_info: ShareBudget, request: Request, response: Response, db: Session = Depends(get_db)):
    authorized_user = db.query(models.User).filter(models.User.session_id == request.cookies.get("session_token")).first()
    if authorized_user:
        for user in share_info.share_target_users:
            if_user_exist = db.query(models.User).filter(models.User.id == user).first()
            if if_user_exist:
                for budget in share_info.budgets_id:
                    if db.get(models.Budget, budget):
                        owner = db.query(models.Budget).filter(models.Budget.id == budget, models.Budget.owner == authorized_user.id).first()
                        if owner:
                            share_exist = db.query(models.Share).filter(models.Share.user == user, models.Share.budget == budget).first()
                            if share_exist:
                                response.status_code = status.HTTP_400_BAD_REQUEST
                                return {f"Bucket with ID: {budget} is already shared to user: {user}"}
                            else:
                                db_share = models.Share(budget=budget, user=user)
                                db.add(db_share)
                        else:
                            response.status_code = status.HTTP_400_BAD_REQUEST
                            return {f"User: {user} is not owner of a budget: {budget}"}
                    else:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                        return {f"Budget: {budget} does not exist"}
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"Target user does not exist"}
        db.commit()
        response.status_code = status.HTTP_201_CREATED
        return {"Shared"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"Unauthorized user"}
