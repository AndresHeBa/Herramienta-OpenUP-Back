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
_PERMISSIONS_STORE = [
    {"action": "create", "roles": ["author", "admin"]},
    {"action": "edit", "roles": ["author", "admin"]},
    {"action": "approve", "roles": ["revisor", "PO", "admin"]},
    {"action": "change_state", "roles": ["revisor", "PO", "admin"]}
]

# Default mapping used as a final fallback to ensure middleware has sensible defaults
_DEFAULT_PERMISSIONS = {p['action']: p['roles'] for p in _PERMISSIONS_STORE}

_ROLES_STORE = [
    {"name": "author", "displayName": "Autor", "description": "Autor de artefactos"},
    {"name": "revisor", "displayName": "Revisor", "description": "Revisa artefactos"},
    {"name": "PO", "displayName": "Product Owner", "description": "Product Owner"},
    {"name": "admin", "displayName": "Administrador", "description": "Administrador"}
]


def _use_db():
    return (not TEST_MODE) and (dbConnLocal is not None)


def fnGetPermissions():
    try:
        if _use_db():
            docs = list(dbConnLocal.clPermissions.find())
            for d in docs:
                d["_id"] = str(d["_id"])
            return {**ResponseMessage.message200, "data": docs}

        return {**ResponseMessage.message200, "data": _PERMISSIONS_STORE}
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetPermissionsByAction(action):
    try:
        if _use_db():
            doc = dbConnLocal.clPermissions.find_one({"action": action})
            if not doc:
                return {**ResponseMessage.message404, "data": "Not found"}
            return {**ResponseMessage.message200, "action": doc["action"], "roles": doc.get("roles", [])}

        for p in _PERMISSIONS_STORE:
            if p["action"] == action:
                return {**ResponseMessage.message200, "action": p["action"], "roles": p.get("roles", [])}
        return {**ResponseMessage.message404, "data": "Not found"}
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnReplacePermissions(data_list):
    try:
        if not isinstance(data_list, list):
            return {**ResponseMessage.message422, "data": "Expected list"}

        if _use_db():
            dbConnLocal.clPermissions.delete_many({})
            for item in data_list:
                item["createdAt"] = datetime.now()
                dbConnLocal.clPermissions.insert_one(item)
            return {**ResponseMessage.message200, "data": data_list}

        # replace in-memory
        global _PERMISSIONS_STORE
        _PERMISSIONS_STORE = [{"action": i.get("action"), "roles": i.get("roles", [])} for i in data_list]
        return {**ResponseMessage.message200, "data": _PERMISSIONS_STORE}
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnPatchPermission(action, roles):
    try:
        if not action or not isinstance(roles, list):
            return {**ResponseMessage.message422, "data": "Invalid payload"}

        if _use_db():
            updated = dbConnLocal.clPermissions.update_one({"action": action}, {"$set": {"roles": roles}}, upsert=True)
            doc = dbConnLocal.clPermissions.find_one({"action": action})
            return {**ResponseMessage.message200, "action": doc["action"], "roles": doc.get("roles", [])}

        found = False
        for p in _PERMISSIONS_STORE:
            if p["action"] == action:
                p["roles"] = roles
                found = True
                break
        if not found:
            _PERMISSIONS_STORE.append({"action": action, "roles": roles})

        return {**ResponseMessage.message200, "action": action, "roles": roles}
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetRoles():
    try:
        if _use_db():
            docs = list(dbConnLocal.clRoles.find())
            for d in docs:
                d["_id"] = str(d["_id"])
            return {**ResponseMessage.message200, "data": docs}
        return {**ResponseMessage.message200, "data": _ROLES_STORE}
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnCreateRole(role_obj):
    try:
        name = role_obj.get('name')
        if not name:
            return {**ResponseMessage.message422, "data": "name required"}

        if _use_db():
            existing = dbConnLocal.clRoles.find_one({"name": name})
            if existing:
                return {**ResponseMessage.message422, "data": "Role exists"}
            dbConnLocal.clRoles.insert_one(role_obj)
            return {**ResponseMessage.message201, "data": role_obj}

        for r in _ROLES_STORE:
            if r.get('name') == name:
                return {**ResponseMessage.message422, "data": "Role exists"}
        _ROLES_STORE.append(role_obj)
        return {**ResponseMessage.message201, "data": role_obj}
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnDeleteRole(name):
    try:
        if not name:
            return ResponseMessage.message422
        if _use_db():
            dbConnLocal.clRoles.delete_one({"name": name})
            return {**ResponseMessage.message200, "message": "Role deleted"}

        global _ROLES_STORE
        _ROLES_STORE = [r for r in _ROLES_STORE if r.get('name') != name]
        return {**ResponseMessage.message200, "message": "Role deleted"}
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetAllowedRoles(action):
    # helper used by middleware
    try:
        if _use_db():
            doc = dbConnLocal.clPermissions.find_one({"action": action})
            if doc and doc.get('roles'):
                return doc.get('roles', [])
            # fallback to in-memory default if DB has no entry
        for p in _PERMISSIONS_STORE:
            if p["action"] == action:
                return p.get('roles', [])
        # final fallback to defaults
        return _DEFAULT_PERMISSIONS.get(action, [])
    except Exception:
        HelperFunctions.PrintException()
        return []
