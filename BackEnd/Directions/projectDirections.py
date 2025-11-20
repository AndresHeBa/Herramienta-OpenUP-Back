from flask import Blueprint, jsonify, request

projectBluePrint = Blueprint('projectBluePrint', __name__, url_prefix='/api/project')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Keys as connectKeys
import BackEnd.GlobalInfo.Helpers as HelperFunctions

#Functions import
import BackEnd.Functions.projectFunctions as callMethod


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

        # Definir las fases predeterminadas de OpenUP
        openup_phases = ["Incepción", "Elaboración", "Construcción", "Transición"]

        # Llamar al método para crear proyecto
        objResult = callMethod.fnPostProject(
            name=projectName,
            identifier=projectIdentifier,
            startDate=startDate,
            description=description,
            responsible=responsible,
            tags=tags,
            phases=openup_phases,
            status="Creado",
            active=active
        )

        return ResponseMessage.message200

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@projectBluePrint.get('/getProjectList')
def getProjectList():
    try:

        objResult = callMethod.fnGetProjectList()

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
def updateProject():
    try:
        # ✅ Normaliza base64 → archivo → strImageUrl
        body = _normalize_json_body()
        if "__error__" in body:
            code, msg = body["__error__"]
            return jsonify({"status": code, "message": msg}), code
        
        strProjectId = "" if("_id" not in body) else body['_id']
        strTitle = "" if("strTitle" not in body) else body['strTitle']
        strFeatures = "" if("strFeatures" not in body) else body['strFeatures']
        strDescription = "" if("strDescription" not in body) else body['strDescription']
        strTitleEng = "" if("strTitleEng" not in body) else body['strTitleEng']
        strFeaturesEng = "" if("strFeaturesEng" not in body) else body['strFeaturesEng']
        strDescriptionEng = "" if("strDescriptionEng" not in body) else body['strDescriptionEng']
        boolActive = True if("boolActive" not in body) else body['boolActive']
        strImgUrl = "" if("strImageUrl" not in body) else body['strImageUrl']
        strIconUrl = "" if("strIconUrl" not in body) else body['strIconUrl']
        
        
        required_validation = any(str(x).strip() == '' for x in [strTitle, strFeatures, strDescription])
        if required_validation:
            return ResponseMessage.message422
        
        objResult = callMethod.fnUpdateProject(strProjectId, strTitle, strFeatures, strDescription, boolActive, strImgUrl, strIconUrl, strTitleEng, strFeaturesEng, strDescriptionEng)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@projectBluePrint.delete('/deleteProject/<strProjectId>')
def deleteProject(strProjectId):
    try:
        
        objResult = callMethod.fnDeleteProject(strProjectId)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
    
# baja logica
@projectBluePrint.put('/deactivateProject/<strProjectId>')
def deactivateProject(strProjectId):
    try:
        
        objResult = callMethod.fnDeactivateProject(strProjectId)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500