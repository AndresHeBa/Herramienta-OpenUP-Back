from flask import Blueprint, jsonify, request

projectBluePrint = Blueprint('projectBluePrint', __name__, url_prefix='/api/project')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Keys as connectKeys
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.GlobalInfo.permissions import requireAction, requireAdmin

#Functions import
import BackEnd.Functions.projectFunctions as callMethod
from bson import ObjectId

def _normalize_json_body():
    """
    Toma el JSON del request, si hay strImageBase64 la guarda como archivo y
    sobreescribe strImageUrl con la URL pública resultante.
    """
    data = request.get_json(silent=True) or {}
    b64 = (data.get("strImageBase64") or "").strip()
    if b64:
        try:
            url = HelperFunctions.save_image_from_base64(b64)
            data["strImageUrl"] = url
            # opcional: limpiar para no guardar basura
            data.pop("strImageBase64", None)
        except ValueError as ve:
            # 422: error de validación (tamaño/tipo)
            return {"__error__": (422, str(ve))}
    return data


@projectBluePrint.post('/postProject')
@requireAction('create')
def postProject():
    try:
        # 📌 Normaliza body JSON
        body = _normalize_json_body()
        if "__error__" in body:
            code, msg = body["__error__"]
            return jsonify({"status": code, "message": msg}), code

        # Datos requeridos para crear un proyecto OpenUP
        projectName = body.get('projectName', '').strip()
        projectIdentifier = body.get('projectIdentifier', '').strip()
        startDate = body.get('startDate', '').strip()
        description = body.get('description', '').strip()
        responsible = body.get('responsible', '').strip()
        tags = body.get('tags', [])   # Puede ser lista o string
        active = body.get('active', True)

        # Validar campos obligatorios
        if not all([projectName, projectIdentifier, startDate]):
            return ResponseMessage.message422

        # Get phases from request or use default OpenUP phases
        phases = body.get('phases', ["Incepción", "Elaboración", "Construcción", "Transición"])
        
        # Get configurationId if provided
        configuration_id = body.get('configurationId')
        
        # HU-022: Get repository information if provided
        repository_url = body.get('repositoryUrl')
        repository_type = body.get('repositoryType', 'git')

        # Llamar al método para crear proyecto
        objResult = callMethod.fnPostProject(
            name=projectName,
            identifier=projectIdentifier,
            startDate=startDate,
            description=description,
            responsible=responsible,
            tags=tags,
            phases=phases,
            configuration_id=configuration_id,
            repository_url=repository_url,
            repository_type=repository_type,
            status="Creado",
            active=active
        )
        

        return objResult

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def convert_objectid(data):
    """Convierte ObjectId a string recursivamente"""
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    return data

@projectBluePrint.get('/getProjectList')
def getProjectList():
    try:
        objResult = callMethod.fnGetProjectList()
        objResult = convert_objectid(objResult)
        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@projectBluePrint.get('/getProject/<strProjectId>')
def getProject(strProjectId):
    try:
        objResult = callMethod.fnGetProject(strProjectId)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@projectBluePrint.put('/updateProject')
@requireAction('edit')
def updateProject():
    try:
        body = request.get_json(silent=True) or {}
        
        projectId = body.get('_id', '').strip()
        projectName = body.get('name', '').strip()
        identifier = body.get('identifier', '').strip()
        startDate = body.get('startDate', '').strip()
        description = body.get('description', '').strip()
        responsible = body.get('responsible', '').strip()
        tags = body.get('tags', [])
        repositoryUrl = body.get('repositoryUrl', '').strip()
        
        # Validar campos obligatorios
        if not all([projectId, projectName, identifier, startDate]):
            return ResponseMessage.message422
        
        objResult = callMethod.fnUpdateOpenUPProject(
            projectId=projectId,
            name=projectName,
            identifier=identifier,
            startDate=startDate,
            description=description,
            responsible=responsible,
            tags=tags,
            repositoryUrl=repositoryUrl
        )

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@projectBluePrint.delete('/deleteProject/<strProjectId>')
@requireAdmin
def deleteProject(strProjectId):
    try:
        
        objResult = callMethod.fnDeleteProject(strProjectId)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
    
# baja logica
@projectBluePrint.put('/deactivateProject/<strProjectId>')
@requireAction('change_state')
def deactivateProject(strProjectId):
    try:
        
        objResult = callMethod.fnDeactivateProject(strProjectId)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500