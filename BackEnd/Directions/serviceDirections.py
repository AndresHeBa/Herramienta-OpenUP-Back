from flask import Blueprint, jsonify, request

serviceBluePrint = Blueprint('serviceBluePrint', __name__, url_prefix='/api/service')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Keys as connectKeys
import BackEnd.GlobalInfo.Helpers as HelperFunctions

#Functions import
import BackEnd.Functions.serviceFunctions as callMethod


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


@serviceBluePrint.post('/postService')
def postService():
    try:
        
        # ✅ Normaliza base64 → archivo → strImageUrl
        body = _normalize_json_body()
        if "__error__" in body:
            code, msg = body["__error__"]
            return jsonify({"status": code, "message": msg}), code

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
        
        
        objResult = callMethod.fnPostService(strTitle, strFeatures, strDescription, boolActive, strImgUrl, strIconUrl, strTitleEng, strFeaturesEng, strDescriptionEng)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@serviceBluePrint.get('/getServiceList')
def getServiceList():
    try:

        objResult = callMethod.fnGetServiceList()

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@serviceBluePrint.get('/getService/<strServiceId>')
def getService(strServiceId):
    try:
        objResult = callMethod.fnGetService(strServiceId)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@serviceBluePrint.put('/updateService')
def updateService():
    try:
        # ✅ Normaliza base64 → archivo → strImageUrl
        body = _normalize_json_body()
        if "__error__" in body:
            code, msg = body["__error__"]
            return jsonify({"status": code, "message": msg}), code
        
        strServiceId = "" if("_id" not in body) else body['_id']
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
        
        objResult = callMethod.fnUpdateService(strServiceId, strTitle, strFeatures, strDescription, boolActive, strImgUrl, strIconUrl, strTitleEng, strFeaturesEng, strDescriptionEng)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

@serviceBluePrint.delete('/deleteService/<strServiceId>')
def deleteService(strServiceId):
    try:
        
        objResult = callMethod.fnDeleteService(strServiceId)

        return jsonify(objResult)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500