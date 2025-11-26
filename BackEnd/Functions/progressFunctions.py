from datetime import datetime
from bson.objectid import ObjectId
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = HelperFunctions.dbConnection()


def fnPostProgress(projectId, iteration, startDate, endDate, tasks, completionPercent, blockers, observations):
    try:
        progress = {
            "projectId": projectId,
            "iteration": iteration,
            "startDate": startDate,
            "endDate": endDate,
            "tasks": tasks,
            "completionPercent": completionPercent,
            "blockers": blockers,
            "observations": observations,
            "creationDate": datetime.now(),
            "version": 1,
            "status": "Registrado"
        }

        progress = HelperFunctions.deleteBlankAttributes(progress)

        # Guardar en colecciones:
        insert_result = dbConnLocal.clProgress.insert_one(progress)

        # Registrar copia histórica
        progress["_id"] = str(insert_result.inserted_id)
        dbConnLocal.clProgressHistory.insert_one(progress)

        return {**ResponseMessage.message201, "insertedId": str(insert_result.inserted_id)}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



def fnGetProgress(projectId):
    try:
        dbResult = list(dbConnLocal.clProgress.find({"projectId": projectId}))
        for result in dbResult:
            result["_id"] = str(result["_id"])

        return {
            **ResponseMessage.message200,
            "Result": dbResult
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateProgress(progressId, updates):
    try:
        if not ObjectId.is_valid(progressId):
            return {**ResponseMessage.message202, "data": "Invalid progress ID"}

        existing = dbConnLocal.clProgress.find_one({"_id": ObjectId(progressId)})
        if not existing:
            return ResponseMessage.message404

        # Actualizar versión
        new_version = existing.get("version", 1) + 1
        updates["version"] = new_version
        updates["modificationDate"] = datetime.now()

        # Guardar nueva versión en clProgress
        dbConnLocal.clProgress.update_one(
            {"_id": ObjectId(progressId)},
            {"$set": updates}
        )

        # Guardar copia histórica con ID referenciado
        history_entry = {
            **existing,
            **updates,
            "_idProgress": str(progressId),
            "_id": str(ObjectId()),
            "historyDate": datetime.now()
        }
        dbConnLocal.clProgressHistory.insert_one(history_entry)

        return {**ResponseMessage.message200, "newVersion": new_version}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



def fnGetSummary(projectId):
    try:
        iterations = list(dbConnLocal.clProgress.find({"projectId": projectId}))
        if not iterations:
            return {**ResponseMessage.message404, "data": "No progress data"}

        total_percent = sum(i.get("completionPercent", 0) for i in iterations) / len(iterations)
        phases_summary = {}

        for i in iterations:
            phase = i.get("iteration", "Fase no definida")
            phases_summary[phase] = i.get("completionPercent", 0)

        return {
            **ResponseMessage.message200,
            "Result": {
                "projectId": projectId,
                "totalCompletionPercent": round(total_percent, 2),
                "progressByPhase": phases_summary,
                "iterationsCount": len(iterations)
            }
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

def fnGetHistory(projectId):
    try:
        history = list(dbConnLocal.clProgressHistory.find(
            {"projectId": projectId},
            {"_id": 0}
        ))

        return {
            **ResponseMessage.message200,
            "history": history
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
