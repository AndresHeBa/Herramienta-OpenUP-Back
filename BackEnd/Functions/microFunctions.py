from datetime import datetime
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from bson.objectid import ObjectId

dbConnLocal = HelperFunctions.dbConnection()


def fnPostMicroincrement(projectId, iteration, deliverable, title, description, date, author, 
                        micro_type=None, evidence=None, value=None):
    try:
        micro = {
            "projectId": projectId,
            "iteration": iteration,
            "deliverable": deliverable,
            "title": title,
            "description": description,
            "date": date,
            "author": author,
            "status": "Registrado",
            "creationDate": datetime.now(),
            "type": micro_type or "funcional",  # Nuevo: técnico o funcional
            "evidence": evidence or "",  # Nuevo: archivo o enlace
            "value": value if value is not None else 0  # Nuevo: valor 0-10
        }

        micro = HelperFunctions.deleteBlankAttributes(micro)

        # Validar campos obligatorios
        if not all([projectId, iteration, title, author]):
            return ResponseMessage.message422

        dbConnLocal.clMicroincrements.insert_one(micro)

        return {**ResponseMessage.message201, "message": "Microincremento registrado exitosamente."}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



def fnGetMicroincrement(microId):
    try:
        if not ObjectId.is_valid(microId):
            return {**ResponseMessage.message202, "data": "invalid microincrement id"}

        result = dbConnLocal.clMicroincrements.find_one({'_id': ObjectId(microId)})
        
        if not result:
            return ResponseMessage.message404
        
        result['_id'] = str(result['_id'])
        return {**ResponseMessage.message200, "result": result}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



def fnGetMicroincrementList(projectId=None, iteration=None, deliverable=None, author=None):
    try:
        query = {}

        # filtros dinámicos
        if projectId:
            query["projectId"] = projectId
        if iteration:
            query["iteration"] = iteration
        if deliverable:
            query["deliverable"] = deliverable
        if author:
            query["author"] = {"$regex": author, "$options": "i"}

        dbResult = list(dbConnLocal.clMicroincrements.find(query))
        count = dbConnLocal.clMicroincrements.count_documents(query)

        for item in dbResult:
            item['_id'] = str(item['_id'])

        return {
            **ResponseMessage.message200,
            "Result": {
                "microincrements": dbResult,
                "length": count
            }
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
