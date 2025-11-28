from datetime import datetime, timedelta
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Keys as connectKeys
import BackEnd.GlobalInfo.Helpers as HelperFunctions

from bson.objectid import ObjectId

dbConnLocal = HelperFunctions.dbConnection()

def fnPostService(strTitle, strFeatures, strDescription, boolActive, strImgUrl, strIconUrl, strTitleEng, strFeaturesEng, strDescriptionEng):
    try:
        
        service = {
            "strTitle": strTitle,
            "strFeatures": strFeatures,
            "strDescription": strDescription,
            "boolActive": boolActive,
            "strImageUrl": strImgUrl,
            "strIconUrl": strIconUrl,
            "strTitleEng": strTitleEng,
            "strFeaturesEng": strFeaturesEng,
            "strDescriptionEng": strDescriptionEng,
            "creationDate": datetime.now()
        }
        
        service = HelperFunctions.deleteBlankAttributes(service)
        
        print(strTitle.strip().lower())
        
        serviceGet = dbConnLocal.clServices.find_one({'strTitle': strTitle})
        
        print(serviceGet)
        
        if serviceGet != None:
            return ResponseMessage.message409
        
        dbConnLocal.clServices.insert_one(service)
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

def fnGetService(strServiceId):
    try:
        
        if not ObjectId.is_valid(strServiceId):
            return {
                **ResponseMessage.message202,
                'data': 'invalid service id'
            }
            
        result = dbConnLocal.clServices.find_one({'_id': ObjectId(strServiceId)})
        
        if result == None:
            return ResponseMessage.message404
        
        return {
            **ResponseMessage.message200,
            'Result': {
                **result,
                '_id': str(result['_id'])
                }
            }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

def fnGetServiceList():
    try:
        
        
        dbResult = list(dbConnLocal.clServices.find({}))
        count = dbConnLocal.clServices.count_documents({})
        
        for result in dbResult:
            result['_id'] = str(result['_id'])
            
        
        return {
            **ResponseMessage.message200,
            'Result': {
                'listResult': dbResult,
                'length': count
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

def fnUpdateService(strServiceId, strTitle, strFeatures, strDescription, boolActive, strImgUrl, strIconUrl, strTitleEng, strFeaturesEng, strDescriptionEng):
    try:
        print(strTitleEng)
        if not ObjectId.is_valid(strServiceId):
            return {
                **ResponseMessage.message202,
                'data': 'invalid service id'
            }
        
        service = dbConnLocal.clServices.find_one({'_id': ObjectId(strServiceId)})
        
        if service == None:
            return ResponseMessage.message404
        
        
        
        result = dbConnLocal.clServices.update_one({'_id': ObjectId(strServiceId)}, {'$set': {
            "strTitle": strTitle,
            "strFeatures": strFeatures,
            "strDescription": strDescription,
            "boolActive": boolActive,
            "strImageUrl": strImgUrl,
            "strIconUrl": strIconUrl,
            "strTitleEng": strTitleEng,
            "strFeaturesEng": strFeaturesEng,
            "strDescriptionEng": strDescriptionEng,
            "modificationDate": datetime.now()
        }})
        
        
        print(result.matched_count)
        print(result.modified_count)
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
    
def fnDeleteService(strServiceId):
    try:
        
        if not ObjectId.is_valid(strServiceId):
            return {
                **ResponseMessage.message202,
                'data': 'invalid testimonial id'
            }
            
        result = dbConnLocal.clServices.find_one({'_id': ObjectId(strServiceId)})
        
        if result == None:
            return ResponseMessage.message404
        
        dbConnLocal.clServices.delete_one({'_id': ObjectId(strServiceId)})
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
    
def fnDeleteProject(strProjectId):
    try:
        
        if not ObjectId.is_valid(strProjectId):
            return {
                **ResponseMessage.message202,
                'data': 'invalid project id'
            }
            
        result = dbConnLocal.clProjects.find_one({'_id': ObjectId(strProjectId)})
        
        if result == None:
            return ResponseMessage.message404
        
        dbConnLocal.clProjects.delete_one({'_id': ObjectId(strProjectId)})
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500