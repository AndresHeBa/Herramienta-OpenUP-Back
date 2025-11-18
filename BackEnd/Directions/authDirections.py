from flask import Blueprint, jsonify, request

authBluePrint = Blueprint('authBluePrint', __name__, url_prefix='/api/auth')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Keys as connectKeys
import BackEnd.GlobalInfo.Helpers as HelperFunctions

#Functions import
import BackEnd.Functions.authFunctions as callMethod

@authBluePrint.post('')
def login():
    try:
        
        strEmail = "" if("strEmail" not in request.json) else request.json['strEmail']
        strPassword = "" if("strPassword" not in request.json) else request.json['strPassword']
        
        required_validation = any(str(x).strip() == '' for x in [strEmail, strPassword])
        if required_validation:
            return ResponseMessage.message422
        
        session = callMethod.login(strEmail, strPassword) 

        return jsonify(session)
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500