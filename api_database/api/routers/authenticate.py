from datetime import timedelta
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database.core import get_db_azure,get_db_sqlite
from database.authenticate import Token, User, UserCreate, authenticate_user, create_db_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, has_access

router = APIRouter(
    prefix="/auth",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/create_user")
def create_user(request: Request, customer: UserCreate, db: Session = Depends(get_db_sqlite)) -> User:
    """Create a new user.

    Args:
        request (Request): The incoming request.
        customer (UserCreate): Information about the user to be created.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_sqlite).

    Returns:
        User: The newly created user.
    """
    db_customer = create_db_user(customer, db)
    return User(**db_customer.__dict__)


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request, db: Session = Depends(get_db_sqlite)) -> Token:    
    """Login to obtain an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form containing user login credentials.
        request (Request): The incoming request.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_sqlite).

    Returns:
        Token: The generated access token."""
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
    return Token(access_token=access_token, token_type="bearer")



@router.get("/is_authorized", response_model=None)
async def is_authorized(current_user: Annotated[User, Depends(has_access)]):
    """Check if the user is authorized to access resources.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        None
    """
    return True