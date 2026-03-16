"""
Auth0 Authentication Module

Handles user authentication and session management with Auth0.
"""

from flask import session, redirect, url_for, request
from authlib.integrations.flask_client import OAuth
import os
from functools import wraps

# Initialize OAuth
oauth = OAuth()


def setup_auth(app):
    """
    Setup Auth0 authentication for the Flask application
    
    Args:
        app: Flask application instance
    """
    oauth.init_app(app)
    
    # Configure Auth0
    oauth.register(
        'auth0',
        client_id=os.getenv('AUTH0_CLIENT_ID'),
        client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
        server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid profile email'
        }
    )
    
    print("[Auth] Auth0 configured successfully")


def requires_auth(f):
    """
    Decorator to require authentication for routes
    Redirects to login if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            # Store the destination URL for redirect after login
            session['next'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Get current user information from session
    
    Returns:
        User info dict if logged in, None otherwise
    """
    user = session.get('user')
    if user:
        return user.get('userinfo', user)
    return None


def is_authenticated():
    """Check if user is currently authenticated"""
    return 'user' in session


def logout_user():
    """
    Logout user from session
    """
    session.clear()


__all__ = ['setup_auth', 'oauth', 'requires_auth', 'get_current_user', 'is_authenticated', 'logout_user']
