
from models import User


def get_user(user_id: str) -> dict:
    """
    Get user by ID and return as dictionary
    
    Args:
        user_id (str): The user ID from Replit authentication
        
    Returns:
        dict: User data or None if not found
    """
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return None
        
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image_url': user.profile_image_url,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or None
    }

def get_user_by_email(email: str) -> dict:
    """
    Get user by email and return as dictionary
    
    Args:
        email (str): The user email
        
    Returns:
        dict: User data or None if not found
    """
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return None
        
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_image_url': user.profile_image_url,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or None
    }
