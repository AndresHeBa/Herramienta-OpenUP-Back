import os
from datetime import datetime
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = None
try:
    dbConnLocal = HelperFunctions.dbConnection()
except Exception:
    dbConnLocal = None

# When running tests set TEST_MODE=1 to use in-memory storage
TEST_MODE = os.environ.get('TEST_MODE') == '1'

# In-memory stores for tests
_USERS_STORE = [
    {
        "_id": "1",
        "username": "admin",
        "email": "admin@openup.com",
        "password": "admin123",
        "roles": ["admin"],
        "active": True,
        "createdAt": datetime.now()
    },
    {
        "_id": "2",
        "username": "autor1",
        "email": "autor@openup.com",
        "password": "autor123",
        "roles": ["author"],
        "active": True,
        "createdAt": datetime.now()
    },
    {
        "_id": "3",
        "username": "revisor1",
        "email": "revisor@openup.com",
        "password": "revisor123",
        "roles": ["revisor"],
        "active": True,
        "createdAt": datetime.now()
    }
]


def _use_db():
    return (not TEST_MODE) and (dbConnLocal is not None)


def fnLogin(username, password):
    """
    Autentica un usuario con username y password.
    Retorna los datos del usuario si las credenciales son válidas.
    """
    try:
        print(f"[LOGIN] Attempting login for username: {username}")
        
        if not username or not password:
            return {**ResponseMessage.message422, "data": "Username and password required"}

        print(f"[LOGIN] Using DB: {_use_db()}, dbConnLocal: {dbConnLocal is not None}")
        
        # Intentar primero en BD si está disponible
        if _use_db():
            user = dbConnLocal.clUsers.find_one({"username": username, "password": password, "active": True})
            if user:
                user["_id"] = str(user["_id"])
                user_copy = dict(user)
                user_copy.pop("password", None)
                print(f"[LOGIN] User found in DB: {user_copy['username']}")
                return {**ResponseMessage.message200, "data": user_copy}
            print("[LOGIN] User not found in DB, trying memory store...")

        # Buscar en memoria (siempre como fallback o si no hay BD)
        print(f"[LOGIN] Searching in memory store, total users: {len(_USERS_STORE)}")
        for user in _USERS_STORE:
            if user["username"] == username and user["password"] == password and user.get("active", True):
                user_copy = user.copy()
                user_copy.pop("password", None)
                print(f"[LOGIN] User found in memory: {user_copy['username']}")
                return {**ResponseMessage.message200, "data": user_copy}
        
        return {**ResponseMessage.message401, "data": "Invalid credentials"}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetUserById(userId):
    """
    Obtiene un usuario por su ID.
    """
    try:
        if not userId:
            return ResponseMessage.message422

        if _use_db():
            from bson import ObjectId
            try:
                user = dbConnLocal.clUsers.find_one({"_id": ObjectId(userId)})
            except:
                user = dbConnLocal.clUsers.find_one({"_id": userId})
            
            if user:
                user["_id"] = str(user["_id"])
                # No devolver la contraseña
                user.pop("password", None)
                return {**ResponseMessage.message200, "data": user}
            return {**ResponseMessage.message404, "data": "User not found"}

        # In-memory search
        for user in _USERS_STORE:
            if user["_id"] == userId:
                user_copy = user.copy()
                user_copy.pop("password", None)
                return {**ResponseMessage.message200, "data": user_copy}
        
        return {**ResponseMessage.message404, "data": "User not found"}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetAllUsers():
    """
    Obtiene todos los usuarios activos (sin contraseñas).
    """
    try:
        if _use_db():
            users = list(dbConnLocal.clUsers.find({"active": True}))
            for user in users:
                user["_id"] = str(user["_id"])
                user.pop("password", None)
            return {**ResponseMessage.message200, "data": users}

        # In-memory
        users = []
        for user in _USERS_STORE:
            if user.get("active", True):
                user_copy = user.copy()
                user_copy.pop("password", None)
                users.append(user_copy)
        
        return {**ResponseMessage.message200, "data": users}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnCreateUser(username, email, password, roles):
    """
    Crea un nuevo usuario.
    """
    try:
        if not all([username, email, password, roles]):
            return {**ResponseMessage.message422, "data": "All fields required"}

        if not isinstance(roles, list):
            return {**ResponseMessage.message422, "data": "Roles must be a list"}

        if _use_db():
            # Verificar si el usuario ya existe
            existing = dbConnLocal.clUsers.find_one({"username": username})
            if existing:
                return {**ResponseMessage.message422, "data": "Username already exists"}

            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "roles": roles,
                "active": True,
                "createdAt": datetime.now()
            }
            result = dbConnLocal.clUsers.insert_one(user_data)
            user_data["_id"] = str(result.inserted_id)
            user_data.pop("password", None)
            return {**ResponseMessage.message201, "data": user_data}

        # In-memory
        for user in _USERS_STORE:
            if user["username"] == username:
                return {**ResponseMessage.message422, "data": "Username already exists"}

        new_user = {
            "_id": str(len(_USERS_STORE) + 1),
            "username": username,
            "email": email,
            "password": password,
            "roles": roles,
            "active": True,
            "createdAt": datetime.now()
        }
        _USERS_STORE.append(new_user)
        
        user_copy = new_user.copy()
        user_copy.pop("password", None)
        return {**ResponseMessage.message201, "data": user_copy}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateUser(userId, updates):
    """
    Actualiza un usuario existente.
    updates puede contener: email, password, roles, active
    """
    try:
        if not userId or not updates:
            return ResponseMessage.message422

        allowed_fields = ["email", "password", "roles", "active"]
        update_data = {k: v for k, v in updates.items() if k in allowed_fields}

        if not update_data:
            return {**ResponseMessage.message422, "data": "No valid fields to update"}

        if _use_db():
            from bson import ObjectId
            try:
                obj_id = ObjectId(userId)
            except:
                obj_id = userId

            result = dbConnLocal.clUsers.update_one({"_id": obj_id}, {"$set": update_data})
            
            if result.matched_count == 0:
                return {**ResponseMessage.message404, "data": "User not found"}

            user = dbConnLocal.clUsers.find_one({"_id": obj_id})
            user["_id"] = str(user["_id"])
            user.pop("password", None)
            return {**ResponseMessage.message200, "data": user}

        # In-memory
        for user in _USERS_STORE:
            if user["_id"] == userId:
                user.update(update_data)
                user_copy = user.copy()
                user_copy.pop("password", None)
                return {**ResponseMessage.message200, "data": user_copy}

        return {**ResponseMessage.message404, "data": "User not found"}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnDeleteUser(userId):
    """
    Desactiva un usuario (baja lógica).
    """
    try:
        if not userId:
            return ResponseMessage.message422

        if _use_db():
            from bson import ObjectId
            try:
                obj_id = ObjectId(userId)
            except:
                obj_id = userId

            result = dbConnLocal.clUsers.update_one({"_id": obj_id}, {"$set": {"active": False}})
            
            if result.matched_count == 0:
                return {**ResponseMessage.message404, "data": "User not found"}

            return {**ResponseMessage.message200, "message": "User deactivated"}

        # In-memory
        for user in _USERS_STORE:
            if user["_id"] == userId:
                user["active"] = False
                return {**ResponseMessage.message200, "message": "User deactivated"}

        return {**ResponseMessage.message404, "data": "User not found"}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500