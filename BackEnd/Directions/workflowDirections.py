from flask import Blueprint, jsonify, request
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.Functions.workflowFunctions as callMethod
from BackEnd.GlobalInfo.permissions import requireAction, requireAdmin

workflowBluePrint = Blueprint('workflowBluePrint', __name__, url_prefix='/api/workflows')

@workflowBluePrint.post('/createWorkflow')
@requireAdmin
def createWorkflow():
    try:
        body = request.get_json() or {}
        name = body.get('name', '').strip()
        description = body.get('description', '').strip()
        states = body.get('states')

        result = callMethod.fnCreateWorkflow(name, description, states)
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@workflowBluePrint.get('/getWorkflows')
def getWorkflows():
    try:
        result = callMethod.fnGetWorkflows()
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@workflowBluePrint.post('/assignArtifactToWorkflow')
@requireAdmin
def assignArtifactToWorkflow():
    try:
        body = request.get_json() or {}
        projectId = body.get('projectId', '').strip()
        artifactType = body.get('artifactType', '').strip()
        workflowId = body.get('workflowId', '').strip()

        result = callMethod.fnAssignArtifactToWorkflow(projectId, artifactType, workflowId)
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@workflowBluePrint.put('/updateArtifactState')
@requireAction('change_state')
def updateArtifactState():
    try:
        body = request.get_json() or {}
        artifactId = body.get('artifactId', '').strip()
        newState = body.get('newState', '').strip()
        userId = body.get('userId', '').strip()
        comments = body.get('comments', '').strip()

        result = callMethod.fnUpdateArtifactState(artifactId, newState, userId, comments)
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@workflowBluePrint.get('/getArtifactWorkflowHistory/<artifactId>')
def getArtifactWorkflowHistory(artifactId):
    try:
        result = callMethod.fnGetArtifactWorkflowHistory(artifactId)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@workflowBluePrint.put('/updateWorkflow/<workflowId>')
@requireAdmin
def updateWorkflow(workflowId):
    try:
        body = request.get_json() or {}
        name = body.get('name', '').strip()
        description = body.get('description', '').strip()
        states = body.get('states')

        result = callMethod.fnUpdateWorkflow(workflowId, name, description, states)
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@workflowBluePrint.delete('/deleteWorkflow/<workflowId>')
@requireAdmin
def deleteWorkflow(workflowId):
    try:
        result = callMethod.fnDeleteWorkflow(workflowId)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
