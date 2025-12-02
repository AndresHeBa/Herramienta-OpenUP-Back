from datetime import datetime, timedelta
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Keys as connectKeys
import BackEnd.GlobalInfo.Helpers as HelperFunctions

from bson.objectid import ObjectId

dbConnLocal = HelperFunctions.dbConnection()

def fnPostProject(name, identifier, startDate, description, responsible, tags, phases, status="Creado", active=True):
    try:

        project = {
            "name": name,
            "identifier": identifier,
            "startDate": startDate,
            "description": description,
            "responsible": responsible,
            "tags": tags,
            "status": status,
            "active": active,
            "phases": [{"name": phase, "status": "Pendiente"} for phase in phases],
            "creationDate": datetime.now()
        }

        # Elimina atributos en blanco o None
        project = HelperFunctions.deleteBlankAttributes(project)

        # Validar que no exista proyecto duplicado por nombre o identificador
        existingProject = dbConnLocal.clProjects.find_one({
            "$or": [{"name": name}, {"identifier": identifier}]
        })

        if existingProject:
            return ResponseMessage.message409  # Proyecto ya existe

        # Insertar en base de datos
        dbConnLocal.clProjects.insert_one(project)

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

def fnGetProjectList():
    try:
        dbResult = list(dbConnLocal.clProjects.find({}))
        count = dbConnLocal.clProjects.count_documents({})
        
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
    
def fnGetProject(strProjectId):
    try:
        
        if not ObjectId.is_valid(strProjectId):
            return {
                **ResponseMessage.message202,
                'data': 'invalid project id'
            }
            
        result = dbConnLocal.clProjects.find_one({'_id': ObjectId(strProjectId)})
        
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
    
def fnDeactivateProject(strProjectId):
    try:
        
        if not ObjectId.is_valid(strProjectId):
            return {
                **ResponseMessage.message202,
                'data': 'invalid project id'
            }
        
        project = dbConnLocal.clProjects.find_one({'_id': ObjectId(strProjectId)})
        
        if project == None:
            return ResponseMessage.message404
        
        
        
        result = dbConnLocal.clProjects.update_one({'_id': ObjectId(strProjectId)}, {'$set': {
            "active": False,
            "modificationDate": datetime.now()
        }})
        
        
        print(result.matched_count)
        print(result.modified_count)
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
    
def fnUpdateProject(strProjectId, strTitle, strFeatures, strDescription, boolActive, strImgUrl, strIconUrl, strTitleEng, strFeaturesEng, strDescriptionEng):
    try:
        print(strTitleEng)
        if not ObjectId.is_valid(strProjectId):
            return {
                **ResponseMessage.message202,
                'data': 'invalid project id'
            }
        
        project = dbConnLocal.clProjects.find_one({'_id': ObjectId(strProjectId)})
        
        if project == None:
            return ResponseMessage.message404
        
        
        
        result = dbConnLocal.clProjects.update_one({'_id': ObjectId(strProjectId)}, {'$set': {
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