from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if current_user.role not in roles:
                return abort(403)  # proíbe acesso se não tiver o role certo
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper