from functools import wraps
from flask import request, jsonify, session
import BackEnd.Functions.permissionsFunctions as permFuncs
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

# simple in-memory cache
_CACHE = {}


def _get_user_roles():
    # PRIORIDAD 1: Header 'X-User-Roles' (más confiable con CORS)
    header = request.headers.get('X-User-Roles')
    if header:
        roles = [r.strip() for r in header.split(',') if r.strip()]
        return roles
    
    # PRIORIDAD 2: Sesión de Flask
    if 'roles' in session:
        roles = session.get('roles')
        if isinstance(roles, list):
            return [r for r in roles]
    
    # PRIORIDAD 3: request.user (si algún middleware lo establece)
    user = getattr(request, 'user', None)
    if user and isinstance(user, dict):
        roles = user.get('roles')
        if isinstance(roles, list):
            return [r for r in roles]

    return None


def requireAction(action):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            roles = _get_user_roles()
            if roles is None:
                return jsonify(ResponseMessage.message401), 401

            if 'admin' in roles:
                return f(*args, **kwargs)

            # check cache first
            allowed = _CACHE.get(action)
            if allowed is None:
                allowed = permFuncs.fnGetAllowedRoles(action) or []
                _CACHE[action] = allowed

            # intersection
            if any(r in allowed for r in roles):
                return f(*args, **kwargs)

            # denied
            try:
                print(f"Permission denied for action '{action}' - user roles: {roles} - allowed: {allowed}")
            except Exception:
                pass
            return jsonify({**ResponseMessage.message403, 'data': f"No tiene permiso para '{action}'"}), 403

        return wrapped
    return decorator


def requireAdmin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        roles = _get_user_roles()
        if roles is None:
            return jsonify(ResponseMessage.message401), 401
        if 'admin' in roles:
            return f(*args, **kwargs)
        return jsonify({**ResponseMessage.message403, 'data': 'Admin role required'}), 403
    return wrapped
