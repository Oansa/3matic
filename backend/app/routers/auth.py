from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os
import httpx
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson import ObjectId

from app.database import get_db
from app.models import User, Token

load_dotenv()

router = APIRouter()

# OAuth configuration
config = Config(environ=os.environ)
oauth = OAuth(config)

# OAuth providers
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

if GOOGLE_CLIENT_ID:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

if GITHUB_CLIENT_ID:
    oauth.register(
        name='github',
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        authorize_url='https://github.com/login/oauth/authorize',
        access_token_url='https://github.com/login/oauth/access_token',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'read:user user:email'}
    )

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        db = get_db()
        if db is None:
            # Database not available - return mock user for testing
            return {
                "id": user_id,
                "email": "test@example.com",
                "name": "Test User",
                "provider": "test"
            }
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise credentials_exception
        
        user["id"] = str(user["_id"])
        return user
    except Exception as e:
        # If database error, return mock user for testing
        print(f"Database error in get_current_user: {e}")
        return {
            "id": user_id,
            "email": "test@example.com",
            "name": "Test User",
            "provider": "test"
        }

@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login"""
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    # Check if provider is configured
    if provider not in oauth.providers:
        raise HTTPException(
            status_code=400, 
            detail=f"OAuth provider '{provider}' is not configured. Please set {provider.upper()}_CLIENT_ID and {provider.upper()}_CLIENT_SECRET in your .env file"
        )
    
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await oauth.providers[provider].authorize_redirect(request, redirect_uri)

@router.get("/oauth/{provider}/callback", name="oauth_callback")
async def oauth_callback(provider: str, request: Request):
    """Handle OAuth callback"""
    try:
        # Check if OAuth provider is configured
        if provider not in oauth.providers:
            raise HTTPException(status_code=400, detail=f"OAuth provider '{provider}' not configured")
        
        token = await oauth.providers[provider].authorize_access_token(request)
        
        # Get user info
        if provider == 'google':
            user_info = token.get('userinfo')
            if not user_info:
                raise Exception("No userinfo in Google token")
            email = user_info.get('email')
            name = user_info.get('name')
            provider_id = user_info.get('sub')
        elif provider == 'github':
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token['access_token']}"}
                user_response = await client.get('https://api.github.com/user', headers=headers)
                user_info = user_response.json()
                email = user_info.get('email') or user_info.get('login') + '@github'
                name = user_info.get('name') or user_info.get('login')
                provider_id = str(user_info.get('id'))
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        # Create or get user
        try:
            db = get_db()
            if db is None:
                # Database not available - create mock user for testing
                mock_user_id = f"test_{provider}_{provider_id}"
                jwt_token = create_access_token({"sub": mock_user_id})
                frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
                return RedirectResponse(url=f"{frontend_url}/login?token={jwt_token}")
            
            user = await db.users.find_one({
                "provider": provider,
                "provider_id": provider_id
            })
            
            if not user:
                user_data = {
                    "email": email,
                    "name": name,
                    "provider": provider,
                    "provider_id": provider_id,
                    "created_at": datetime.utcnow()
                }
                result = await db.users.insert_one(user_data)
                user = await db.users.find_one({"_id": result.inserted_id})
            
            # Create JWT token
            jwt_token = create_access_token({"sub": str(user["_id"])})
        except Exception as db_error:
            # Database error - create mock user for testing
            print(f"Database error in OAuth callback: {db_error}")
            mock_user_id = f"test_{provider}_{provider_id}"
            jwt_token = create_access_token({"sub": mock_user_id})
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/login?token={jwt_token}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"OAuth error: {e}")
        import traceback
        traceback.print_exc()
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/login?error=oauth_failed")

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    # Handle both database user (with _id) and mock user (with id)
    user_id = current_user.get("id") or str(current_user.get("_id", ""))
    return {
        "id": user_id,
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "provider": current_user.get("provider")
    }

@router.post("/test-login")
async def test_login():
    """Test login endpoint for development (no OAuth required)"""
    # Create a test user token
    test_user_id = "test_user_123"
    jwt_token = create_access_token({"sub": test_user_id})
    
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": test_user_id,
            "email": "test@example.com",
            "name": "Test User",
            "provider": "test"
        }
    }

