"""This module defines decorators to be used to wrap functions (excluding auth)."""
from functools import wraps
from flask import request, jsonify
from app.models import User
from app.extensions import db
from auth.auth import requires_auth, get_token_auth_header

def user_required(f):
    """
    A decorator that ensures a user exists for the given Auth0 ID.
    
    This decorator wraps another function and does the following:
    1. Requires authentication using the 'get:games' permission.
    2. Retrieves the Auth0 ID from the authentication payload.
    3. Looks up the user in the database using the Auth0 ID.
    4. If the user doesn't exist, creates a new user with information from the payload.
    5. Adds the user object to the kwargs of the wrapped function.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    The decorated function will have an additional 'user' argument containing the User object.
    """
    @wraps(f)
    @requires_auth('get:games')
    def decorated_function(payload, *args, **kwargs):
        auth0_id = payload['sub']
        user = User.query.filter_by(auth0_id=auth0_id).first()
        
        if not user:
            # Create a new user
            new_user = User(
                username=payload.get('nickname', 'New User'),
                email=payload.get('email', 'No email provided'),
                auth0_id=auth0_id
            )
            db.session.add(new_user)
            db.session.commit()
            user = new_user

        # Add the user to the kwargs
        kwargs['user'] = user
        return f(*args, **kwargs)
    return decorated_function
