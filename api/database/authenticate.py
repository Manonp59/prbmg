from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .core import DBUsers, DBToken, NotFoundError, get_db_azure, get_db_sqlite
from typing import Annotated
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Token(BaseModel):
    """Model for the access token"""
    access_token: str
    token_type: str

class User(BaseModel):
    """Model for user data"""
    username: str
    email: str | None = None
    full_name: str | None = None

class UserCreate(BaseModel):
    """Model for the creating new users"""
    username: str
    email: str
    full_name: str
    password: str

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Oauth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_db_user(user: UserCreate,  session: Session) -> DBUsers:
    """Create a new user in the database

    Args:
        user (UserCreate): informations about user to create
        session (Session): SQLAlchemy session to interact with the database

    Returns:
        DBUsers: database user created 
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(user.password)
    db_user = DBUsers(
            username = user.username,
            email = user.email,
            full_name = user.full_name,
            hashed_password = hashed_password 
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

def verify_password(plain_password, hashed_password) -> bool:
    """Verify a plain password against its hashed version.

    Args:
        plain_password (str): Plain text password.
        hashed_password (str): Hashed password.

    Returns:
        bool: True if the plain password matches the hashed password, False otherwise.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Hash a password.

    Args:
        password (str): Plain text password.

    Returns:
        str: Hashed password.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def get_user(username: str, session: Session) -> DBUsers:
    """Get a user from the database by username.

    Args:
        username (str): Username of the user to retrieve.
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        DBUsers: Database user object.
        
    Raises:
        NotFoundError: If the user with the given username is not found.
    """
    db_user = session.query(DBUsers).filter(DBUsers.username == username).first()
    if db_user is None:
        raise NotFoundError(f"User with username {username} not found.")
    return db_user

def authenticate_user(session: Session, username: str, password: str) -> DBUsers:
    """Authenticate a user with a username and password.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        username (str): Username of the user to authenticate.
        password (str): Password of the user to authenticate.

    Returns:
        DBUsers: Database user object if authentication is successful, False otherwise.
    """
    db_user = get_user(username, session)
    if not db_user:
        return False
    if not verify_password(password, db_user.hashed_password):
        return False
    return db_user

def create_access_token(data: dict, expires_delta: timedelta | None = None)-> str:
    """Create an access token.

    Args:
        data (dict): Data to encode into the token.
        expires_delta (timedelta, optional): Expiry duration of the token. Defaults to None.

    Returns:
        str: Encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def has_access(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_db_sqlite)) -> bool:
    """Check if a user has access using an access token.

    Args:
        token (str): Access token.
        session (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_sqlite).

    Raises:
        HTTPException: If access is not authorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = DBToken(username=username)
    except JWTError:
        raise credentials_exception
    db_user = get_user(username=token_data.username,session=session)
    if db_user is None:
        raise credentials_exception
    return True