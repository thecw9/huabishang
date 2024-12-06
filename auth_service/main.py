from fastapi import Depends, FastAPI, HTTPException
import jwt
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import delete, func, insert, select, update
from contextlib import asynccontextmanager


from models import AuthUser
from database import engine, SessionLocal, Base

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_auth_user()
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)


app.title = "User Auth and Management API"


def init_auth_user():
    # AuthUser
    with Session(engine) as session:
        # check user is exist
        statement = select(AuthUser).where(AuthUser.username == "admin")
        user = session.execute(statement).scalar_one_or_none()

        if not user:
            # Create a default user
            user = AuthUser(
                username="admin",
                password="admin",
                email="admin@mail.com",
                access_token=jwt.encode(
                    {"username": "admin"}, "secret", algorithm="HS256"
                ),
                privilege=0,
            )
            session.add(user)
            session.commit()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    privilege: int = 0


@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # check if user already exists
    query = select(AuthUser).where(AuthUser.username == user.username)
    result = db.execute(query).scalar()
    if result:
        raise HTTPException(status_code=400, detail="User already exists")

    # create user
    query = insert(AuthUser).values(
        username=user.username,
        password=user.password,
        email=user.email,
        access_token=jwt.encode(
            {"username": user.username}, "secret", algorithm="HS256"
        ),
        privilege=user.privilege,
    )
    db.execute(query)
    db.commit()

    return {"code": 200, "message": "User created successfully"}


@app.get("/users/")
def get_users(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    query = select(AuthUser).limit(limit).offset((page - 1) * limit)
    result = db.execute(query).scalars().all()

    # query total count
    query = select(func.count(AuthUser.id))
    total = db.execute(query).scalar()

    return {
        "code": 200,
        "message": "Users fetched successfully",
        "data": result,
        "total": total,
    }


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    query = select(AuthUser).where(AuthUser.id == user_id)
    result = db.execute(query).scalar()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "code": 200,
        "message": "User fetched successfully",
        "data": result,
    }


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    query = select(AuthUser).where(AuthUser.id == user_id)
    result = db.execute(query).scalar()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    query = (
        update(AuthUser)
        .where(AuthUser.id == user_id)
        .values(
            username=user.username,
            password=user.password,
            email=user.email,
            privilege=user.privilege,
        )
    )
    db.execute(query)
    db.commit()

    return {"code": 200, "message": "User updated successfully"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    query = select(AuthUser).where(AuthUser.id == user_id)
    result = db.execute(query).scalar()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    query = delete(AuthUser).where(AuthUser.id == user_id)
    db.execute(query)
    db.commit()

    return {"code": 200, "message": "User deleted successfully"}


@app.get("/users/search/")
def search_user(
    username: str, page: int = 1, limit: int = 10, db: Session = Depends(get_db)
):
    query = (
        select(AuthUser)
        .where(AuthUser.username.like(f"%{username}%"))
        .limit(limit)
        .offset((page - 1) * limit)
    )
    result = db.execute(query).scalars().all()

    # query total count
    query = select(func.count(AuthUser.id)).where(
        AuthUser.username.like(f"%{username}%")
    )
    total = db.execute(query).scalar()

    return {
        "code": 200,
        "message": "Users fetched successfully",
        "data": result,
        "total": total,
    }


@app.post("/access_token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    query = select(AuthUser).where(AuthUser.username == form_data.username)
    user = db.execute(query).scalar()

    if not user or user.deleted_at:
        raise HTTPException(status_code=400, detail="Incorrect username")

    # check password
    if user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"code": 200, "message": "Login successful", "data": user}


@app.get("/verify-token")
def verify_token(token: str, db: Session = Depends(get_db)):
    query = select(AuthUser).where(AuthUser.token == token)
    user = db.execute(query).scalar()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    return {"code": 200, "message": "Token verified", "data": user}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
