from datetime import datetime
from bson.objectid import ObjectId
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = HelperFunctions.dbConnection()


def fnPostPlan(projectId, objectives, scope, initialSchedule, phaseResponsibles, milestones, observations, version):
    try:
        plan = {
            "projectId": projectId,
            "objectives": objectives,
            "scope": scope,
            "initialSchedule": initialSchedule,
            "phaseResponsibles": phaseResponsibles,
            "milestones": milestones,
            "observations": observations,
            "version": version,
            "creationDate": datetime.now(),
            "status": "Versión Inicial",
        }

        plan = HelperFunctions.deleteBlankAttributes(plan)

        # Verificar si ya existe plan asociado al proyecto
        existing = dbConnLocal.clPlans.find_one({
            "projectId": projectId,
            "version": version
        })
        if existing:
            return ResponseMessage.message409

        dbConnLocal.clPlans.insert_one(plan)

        return ResponseMessage.message200

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetPlan(projectId):
    try:
        dbResult = list(dbConnLocal.clPlans.find({"projectId": projectId}))
        for result in dbResult:
            result["_id"] = str(result["_id"])

        return {
            **ResponseMessage.message200,
            "Result": dbResult
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdatePlan(planId, updates):
    try:
        if not ObjectId.is_valid(planId):
            return {**ResponseMessage.message202, "data": "invalid plan id"}

        result = dbConnLocal.clPlans.update_one(
            {"_id": ObjectId(planId)},
            {"$set": {**updates, "modificationDate": datetime.now()}}
        )

        if result.matched_count == 0:
            return ResponseMessage.message404

        return ResponseMessage.message200

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
