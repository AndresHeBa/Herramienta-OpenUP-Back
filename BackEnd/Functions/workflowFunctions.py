from datetime import datetime
from bson import ObjectId
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = HelperFunctions.dbConnection()

def fnCreateWorkflow(name, description, states):
    try:
        if not name or not states or not isinstance(states, list):
            return {**ResponseMessage.message422, "data": "Name and states (list) are required"}

        workflow = {
            "name": name,
            "description": description,
            "states": states, # List of strings or objects defining the columns
            "createdAt": datetime.now(),
            "isActive": True
        }

        result = dbConnLocal.clWorkflows.insert_one(workflow)
        
        return {
            **ResponseMessage.message201,
            "message": "Workflow created successfully",
            "workflowId": str(result.inserted_id)
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetWorkflows():
    try:
        workflows = list(dbConnLocal.clWorkflows.find({"isActive": True}))
        for w in workflows:
            w["_id"] = str(w["_id"])
        
        return {**ResponseMessage.message200, "Result": workflows}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnAssignArtifactToWorkflow(projectId, artifactType, workflowId):
    try:
        if not projectId or not artifactType or not workflowId:
            return ResponseMessage.message422

        # Verify workflow exists
        if not ObjectId.is_valid(workflowId):
             return {**ResponseMessage.message422, "data": "Invalid workflowId"}
             
        workflow = dbConnLocal.clWorkflows.find_one({"_id": ObjectId(workflowId)})
        if not workflow:
            return {**ResponseMessage.message404, "data": "Workflow not found"}

        # Upsert assignment config
        # This defines that for a given project and artifact type, this workflow applies
        assignment = {
            "projectId": projectId,
            "artifactType": artifactType,
            "workflowId": workflowId,
            "workflowName": workflow["name"],
            "updatedAt": datetime.now()
        }

        dbConnLocal.clArtifactWorkflowAssignments.update_one(
            {"projectId": projectId, "artifactType": artifactType},
            {"$set": assignment},
            upsert=True
        )

        return {**ResponseMessage.message200, "message": "Artifact assigned to workflow successfully"}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateArtifactState(artifactId, newState, userId, comments=None):
    try:
        if not artifactId or not newState or not userId:
            return ResponseMessage.message422

        if not ObjectId.is_valid(artifactId):
             return {**ResponseMessage.message422, "data": "Invalid artifactId"}

        # Verify artifact exists
        artifact = dbConnLocal.clArtifacts.find_one({"_id": ObjectId(artifactId)})
        if not artifact:
            return {**ResponseMessage.message404, "data": "Artifact not found"}

        # Record history
        history_entry = {
            "artifactId": artifactId,
            "previousState": artifact.get("workflowState"),
            "newState": newState,
            "userId": userId,
            "comments": comments,
            "timestamp": datetime.now()
        }
        dbConnLocal.clArtifactWorkflowHistory.insert_one(history_entry)

        # Update artifact state
        dbConnLocal.clArtifacts.update_one(
            {"_id": ObjectId(artifactId)},
            {"$set": {"workflowState": newState, "workflowStateUpdatedAt": datetime.now()}}
        )

        return {**ResponseMessage.message200, "message": "Artifact state updated successfully"}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetArtifactWorkflowHistory(artifactId):
    try:
        if not ObjectId.is_valid(artifactId):
             return {**ResponseMessage.message422, "data": "Invalid artifactId"}

        history = list(dbConnLocal.clArtifactWorkflowHistory.find({"artifactId": artifactId}).sort("timestamp", -1))
        
        for h in history:
            h["_id"] = str(h["_id"])
            
        return {**ResponseMessage.message200, "Result": history}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
