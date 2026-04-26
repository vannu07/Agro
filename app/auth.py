import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask import session, redirect, url_for, request
from functools import wraps

load_dotenv()

oauth = OAuth()

def setup_auth(app):
    # oauth.init_app(app) # Disabled for review
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key-123")

    # oauth.register( ... ) # Disabled for review
    pass

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Authentication bypassed for Review Mode
        if "user" not in session:
            session["user"] = {
                "userinfo": {
                    "name": "Reviewer",
                    "email": "reviewer@example.com",
                    "picture": url_for('static', filename='images/farmiq_logo_transparent_final_1773573015823.png')
                }
            }
        return f(*args, **kwargs)
    return decorated
