from datetime import datetime, timedelta
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Keys as connectKeys
import BackEnd.GlobalInfo.Helpers as HelperFunctions

from bson.objectid import ObjectId
import jwt

dbConnLocal = HelperFunctions.dbConnection()

def login(strEmail, strPassword):
    try:
        
        hashedPass = HelperFunctions.passwordHash(strPassword)
        
        response = {
            'strName': 1,
            'strRole': 1
        }
       
        user = dbConnLocal.clUsers.find_one({'strEmail': strEmail.lower().strip(), 'strPassword': hashedPass}, response)

        if user == None:
            return ResponseMessage.message404
        
        tokenInfo = {'id': str(user['_id'])}

        tokenInfo = HelperFunctions.deleteBlankAttributes(tokenInfo)

        token = jwt.encode(tokenInfo, connectKeys.tokenPassword, algorithm='HS256')
        
        user['_id'] = str(user['_id'])

        return {
            **ResponseMessage.message200,
            'token': token,
            'Result': user
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500