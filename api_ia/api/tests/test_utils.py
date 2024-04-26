from api_ia.api.utils import generate_token, has_access
from datetime import timedelta, datetime, timezone
import os
import pytest
from jose import jwt
from dotenv import load_dotenv
from fastapi.security import  HTTPAuthorizationCredentials


def test_generate_token():
    # Define mock data and expires_delta
    load_dotenv()
    SECRET_KEY = os.environ.get("API_IA_SECRET_KEY")
    print(SECRET_KEY)
    ALGORITHM = "HS256"
    expires_delta = timedelta(minutes=30)
    # Call the function to generate the token
    token = generate_token("admin")

    # Decode the token to inspect its contents
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # Assert that the token was generated correctly
    assert decoded_token["sub"] == "admin"

@pytest.mark.asyncio
async def test_get_has_access():
    access_token = generate_token("admin")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token)
    is_auth = await has_access(credentials)
    assert isinstance(is_auth, bool)
    assert is_auth == True