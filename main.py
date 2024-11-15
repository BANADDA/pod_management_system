# main.py
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    get_db,
)
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from schemas import Token, UserCreate, UserOut, PodCreate, PodOut
from database import engine, Base, database
from models import User, Pod
from sqlalchemy.orm import Session
from docker_manager import create_container, get_container_status, stop_container
from scheduler import schedule_container_stop

import uvicorn

app = FastAPI()


# Create all tables
Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Obtain a JWT token by providing username and password.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/pods", response_model=PodOut)
def create_pod_endpoint(
    pod: PodCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new pod (Docker container) that runs for a specified duration.
    """
    container_id = create_container(current_user.username)
    expires_at = datetime.utcnow() + timedelta(minutes=pod.duration_minutes)
    new_pod = Pod(
        container_id=container_id,
        user_id=current_user.id,
        expires_at=expires_at,
        status="running",
    )
    db.add(new_pod)
    db.commit()
    db.refresh(new_pod)
    schedule_container_stop(new_pod.id, container_id, pod.duration_minutes)
    return new_pod


@app.get("/pods/{pod_id}", response_model=PodOut)
def get_pod_status_endpoint(
    pod_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve the status of a specific pod.
    """
    pod = db.query(Pod).filter(Pod.id == pod_id, Pod.user_id == current_user.id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    pod.status = get_container_status(pod.container_id)
    db.commit()
    db.refresh(pod)
    return pod


@app.delete("/pods/{pod_id}")
def delete_pod_endpoint(
    pod_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Terminate a specific pod.
    """
    pod = db.query(Pod).filter(Pod.id == pod_id, Pod.user_id == current_user.id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    success = stop_container(pod.container_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pod not found or already stopped")
    pod.status = "stopped"
    db.commit()
    return {"detail": "Pod terminated"}


# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Optional: Uncomment the following lines to run the server directly with this script
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
