from flask import Blueprint, jsonify, request
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.Functions.permissionsFunctions as callMethod
import BackEnd.GlobalInfo.permissions as permissions

permissionsBluePrint = Blueprint('permissionsBluePrint', __name__, url_prefix='/api/permisos')


@permissionsBluePrint.get('/permissions')
def getPermissions():
    try:
        result = callMethod.fnGetPermissions()
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@permissionsBluePrint.get('/permissions/<action>')
def getPermissionsByAction(action):
    try:
        result = callMethod.fnGetPermissionsByAction(action)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@permissionsBluePrint.put('/permissions')
#@permissions.requireAdmin
def replacePermissions():
    try:
        body = request.get_json() or {}
        data = body.get('data')
        result = callMethod.fnReplacePermissions(data)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@permissionsBluePrint.patch('/permissions/<action>')
@permissions.requireAdmin
def patchPermission(action):
    try:
        body = request.get_json() or {}
        roles = body.get('roles')
        result = callMethod.fnPatchPermission(action, roles)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@permissionsBluePrint.get('/roles')
def getRoles():
    try:
        result = callMethod.fnGetRoles()
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@permissionsBluePrint.post('/roles')
#@permissions.requireAdmin
def createRole():
    try:
        body = request.get_json() or {}
        result = callMethod.fnCreateRole(body)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@permissionsBluePrint.delete('/roles/<name>')
@permissions.requireAdmin
def deleteRole(name):
    try:
        result = callMethod.fnDeleteRole(name)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@permissionsBluePrint.patch('/roles/<name>')
@permissions.requireAdmin
def updateRole(name):
    try:
        body = request.get_json() or {}
        result = callMethod.fnUpdateRole(name, body)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
