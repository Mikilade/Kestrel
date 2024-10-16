from functools import wraps
from flask import request, jsonify
from app.models import User
from app.extensions import db
from auth.auth import requires_auth, get_token_auth_header

def user_required(f):
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
