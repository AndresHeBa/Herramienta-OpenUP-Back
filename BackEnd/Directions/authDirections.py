from flask import Blueprint, jsonify, request, session

authBluePrint = Blueprint('authBluePrint', __name__, url_prefix='/api/auth')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.GlobalInfo.permissions import requireAdmin

#Functions import
import BackEnd.Functions.authFunctions as callMethod


@authBluePrint.post('/login')
def login():
    try:
        body = request.get_json() or {}
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        
        if not username or not password:
            return ResponseMessage.message422
        
        result = callMethod.fnLogin(username, password)
        
        print(f"[AUTH ENDPOINT] Login result: {result}")
        print(f"[AUTH ENDPOINT] intCode in result: {result.get('intCode')}")
        
        if result.get('intCode') == 200:
            user = result.get('data')
            # Guardar en sesión
            session.permanent = True  # Hacer la sesión permanente
            session['user_id'] = user['_id']
            session['username'] = user['username']
            session['roles'] = user['roles']
            session['email'] = user.get('email', '')
            
            print(f"[AUTH ENDPOINT] Session saved for user: {user['username']}")
            print(f"[AUTH ENDPOINT] Session ID: {session.get('_id', 'No ID')}")
            print(f"[AUTH ENDPOINT] Session data: {dict(session)}")
            
            # No devolver la contraseña
            user.pop('password', None)
            
            return jsonify(result)
        
        print(f"[AUTH ENDPOINT] Returning error status: {result.get('intCode', 401)}")
        return jsonify(result), result.get('intCode', 401)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@authBluePrint.post('/logout')
def logout():
    try:
        session.clear()
        return jsonify({**ResponseMessage.message200, "message": "Logged out successfully"})
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@authBluePrint.get('/current-user')
def getCurrentUser():
    try:
        if 'user_id' not in session:
            return jsonify({**ResponseMessage.message401, "data": "No active session"}), 401
        
        user_data = {
            "_id": session.get('user_id'),
            "username": session.get('username'),
            "email": session.get('email'),
            "roles": session.get('roles', [])
        }
        
        return jsonify({**ResponseMessage.message200, "data": user_data})
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@authBluePrint.get('/users')
@requireAdmin
def getAllUsers():
    try:
        result = callMethod.fnGetAllUsers()
        return jsonify(result)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@authBluePrint.get('/users/<userId>')
def getUserById(userId):
    try:
        result = callMethod.fnGetUserById(userId)
        return jsonify(result)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@authBluePrint.post('/users')
@requireAdmin
def createUser():
    try:
        body = request.get_json() or {}
        username = body.get('username', '').strip()
        email = body.get('email', '').strip()
        password = body.get('password', '').strip()
        roles = body.get('roles', [])
        
        if not all([username, email, password, roles]):
            return ResponseMessage.message422
        
        result = callMethod.fnCreateUser(username, email, password, roles)
        return jsonify(result), result.get('intCode', 200)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@authBluePrint.put('/users/<userId>')
@requireAdmin
def updateUser(userId):
    try:
        body = request.get_json() or {}
        updates = {
            k: v for k, v in body.items() 
            if k in ['email', 'password', 'roles', 'active']
        }
        
        if not updates:
            return ResponseMessage.message422
        
        result = callMethod.fnUpdateUser(userId, updates)
        return jsonify(result), result.get('intCode', 200)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@authBluePrint.delete('/users/<userId>')
@requireAdmin
def deleteUser(userId):
    try:
        result = callMethod.fnDeleteUser(userId)
        return jsonify(result), result.get('intCode', 200)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500