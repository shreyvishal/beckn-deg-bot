from fastapi import APIRouter, Depends, status
from models.user import UserCreate, UserLogin, UserResponse
from controllers.auth_controllers import (
    register_controller,
    login_controller,
    get_current_user_controller,
    logout_controller,
    auth_health_check_controller
)
from middleware.auth_middleware import get_current_active_user

# Create auth router
router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def auth_health_check():
    """Auth service health check endpoint"""
    return auth_health_check_controller()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """User registration endpoint"""
    return register_controller(user_data)

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_credentials: UserLogin):
    """User login endpoint"""
    return login_controller(user_credentials)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """User logout endpoint"""
    return logout_controller()

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user profile endpoint"""
    return get_current_user_controller(current_user) 