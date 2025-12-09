from datetime import datetime
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = None
try:
    dbConnLocal = HelperFunctions.dbConnection()
except Exception:
    dbConnLocal = None

# In-memory store for testing
_DEFECTS_STORE = []
_DEFECT_COUNTER = 1

def _use_db():
    return dbConnLocal is not None


def _generate_defect_id(projectId):
    global _DEFECT_COUNTER
    if _use_db():
        count = dbConnLocal.clDefects.count_documents({"projectId": projectId})
        return f"DEF-{count + 1:03d}"
    else:
        defect_id = f"DEF-{_DEFECT_COUNTER:03d}"
        _DEFECT_COUNTER += 1
        return defect_id


def fnCreateDefect(projectId, title, description, severity, priority, testCaseId, testExecutionId, 
                   artifactId, artifactName, artifactVersion, reportedBy, assignedTo, stepsToReproduce, environment):
    try:
        defect = {
            "defectId": _generate_defect_id(projectId),
            "projectId": projectId,
            "title": title,
            "description": description,
            "severity": severity,  # Crítica, Alta, Media, Baja
            "status": "Abierto",
            "priority": priority,  # Urgente, Alta, Media, Baja
            "testCaseId": testCaseId,
            "testExecutionId": testExecutionId,
            "artifactId": artifactId,
            "artifactName": artifactName,
            "artifactVersion": artifactVersion,
            "reportedBy": reportedBy,
            "assignedTo": assignedTo,
            "reportedAt": datetime.now(),
            "updatedAt": datetime.now(),
            "stepsToReproduce": stepsToReproduce,
            "environment": environment,
            "attachments": [],
            "comments": [],
            "history": []
        }
        
        if _use_db():
            result = dbConnLocal.clDefects.insert_one(defect)
            defect["_id"] = str(result.inserted_id)
        else:
            defect["_id"] = str(len(_DEFECTS_STORE) + 1)
            _DEFECTS_STORE.append(defect)
        
        return {**ResponseMessage.message200, "data": defect}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetDefectsByProject(projectId):
    try:
        if _use_db():
            defects = list(dbConnLocal.clDefects.find({"projectId": projectId}))
            for d in defects:
                d["_id"] = str(d["_id"])
            return {**ResponseMessage.message200, "data": defects}
        else:
            defects = [d for d in _DEFECTS_STORE if d["projectId"] == projectId]
            return {**ResponseMessage.message200, "data": defects}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetDefectById(defectId):
    try:
        if _use_db():
            from bson import ObjectId
            defect = dbConnLocal.clDefects.find_one({"_id": ObjectId(defectId)})
            if defect:
                defect["_id"] = str(defect["_id"])
                return {**ResponseMessage.message200, "data": defect}
            return {**ResponseMessage.message404, "data": "Defect not found"}
        else:
            defect = next((d for d in _DEFECTS_STORE if d["_id"] == defectId), None)
            if defect:
                return {**ResponseMessage.message200, "data": defect}
            return {**ResponseMessage.message404, "data": "Defect not found"}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateDefect(defectId, updates, changedBy):
    try:
        if _use_db():
            from bson import ObjectId
            defect = dbConnLocal.clDefects.find_one({"_id": ObjectId(defectId)})
            if not defect:
                return {**ResponseMessage.message404, "data": "Defect not found"}
            
            # Registrar cambios en el historial
            history_entries = []
            for field, newValue in updates.items():
                if field in defect and defect[field] != newValue:
                    history_entries.append({
                        "changedBy": changedBy,
                        "changedAt": datetime.now(),
                        "field": field,
                        "oldValue": str(defect[field]),
                        "newValue": str(newValue)
                    })
            
            if history_entries:
                updates["history"] = defect.get("history", []) + history_entries
            
            updates["updatedAt"] = datetime.now()
            
            # Actualizar fechas especiales
            if updates.get("status") == "Resuelto" and "resolvedAt" not in updates:
                updates["resolvedAt"] = datetime.now()
            if updates.get("status") == "Cerrado" and "closedAt" not in updates:
                updates["closedAt"] = datetime.now()
            
            dbConnLocal.clDefects.update_one({"_id": ObjectId(defectId)}, {"$set": updates})
            
            updated_defect = dbConnLocal.clDefects.find_one({"_id": ObjectId(defectId)})
            updated_defect["_id"] = str(updated_defect["_id"])
            return {**ResponseMessage.message200, "data": updated_defect}
        
        else:
            defect = next((d for d in _DEFECTS_STORE if d["_id"] == defectId), None)
            if not defect:
                return {**ResponseMessage.message404, "data": "Defect not found"}
            
            # Registrar cambios en el historial
            history_entries = []
            for field, newValue in updates.items():
                if field in defect and defect[field] != newValue:
                    history_entries.append({
                        "changedBy": changedBy,
                        "changedAt": datetime.now(),
                        "field": field,
                        "oldValue": str(defect[field]),
                        "newValue": str(newValue)
                    })
            
            if history_entries:
                defect["history"] = defect.get("history", []) + history_entries
            
            defect.update(updates)
            defect["updatedAt"] = datetime.now()
            
            if updates.get("status") == "Resuelto" and "resolvedAt" not in defect:
                defect["resolvedAt"] = datetime.now()
            if updates.get("status") == "Cerrado" and "closedAt" not in defect:
                defect["closedAt"] = datetime.now()
            
            return {**ResponseMessage.message200, "data": defect}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnAddCommentToDefect(defectId, author, comment):
    try:
        comment_entry = {
            "author": author,
            "comment": comment,
            "createdAt": datetime.now()
        }
        
        if _use_db():
            from bson import ObjectId
            dbConnLocal.clDefects.update_one(
                {"_id": ObjectId(defectId)},
                {"$push": {"comments": comment_entry}}
            )
            defect = dbConnLocal.clDefects.find_one({"_id": ObjectId(defectId)})
            defect["_id"] = str(defect["_id"])
            return {**ResponseMessage.message200, "data": defect}
        else:
            defect = next((d for d in _DEFECTS_STORE if d["_id"] == defectId), None)
            if not defect:
                return {**ResponseMessage.message404, "data": "Defect not found"}
            
            if "comments" not in defect:
                defect["comments"] = []
            defect["comments"].append(comment_entry)
            return {**ResponseMessage.message200, "data": defect}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
