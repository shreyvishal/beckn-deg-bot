from fastapi import HTTPException, status
from datetime import timedelta
from models.user import UserCreate, UserLogin, UserResponse, user_service
from utils.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


def register_controller(user_data: UserCreate) -> dict:
    """Handle user registration"""
    try:
        # Create user
        user = user_service.create_user(user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meter ID or Email already registered"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "data": {
                "user": user.dict(),
                "access_token": access_token,
                "token_type": "bearer"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


def login_controller(user_credentials: UserLogin) -> dict:
    """Handle user login"""
    try:
        # Authenticate user
        user = user_service.authenticate_user(
            user_credentials.meter_id, 
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect meter ID or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "user": user.dict(),
                "access_token": access_token,
                "token_type": "bearer"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


def get_current_user_controller(current_user: UserResponse) -> dict:
    """Get current user profile"""
    return {
        "status": "success",
        "message": "User profile retrieved successfully",
        "data": {
            "user": current_user.dict()
        }
    }


def logout_controller() -> dict:
    """Handle user logout"""
    # Since we're using JWT tokens, logout is handled client-side
    # by removing the token from storage
    return {
        "status": "success",
        "message": "Logout successful"
    }


def auth_health_check_controller() -> dict:
    """Auth service health check"""
    return {
        "status": "healthy",
        "message": "Auth service is running"
    } 