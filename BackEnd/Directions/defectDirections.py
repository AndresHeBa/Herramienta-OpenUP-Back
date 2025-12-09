from flask import Blueprint, jsonify, request

defectBluePrint = Blueprint('defectBluePrint', __name__, url_prefix='/api/defect')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.GlobalInfo.permissions import requireAction

import BackEnd.Functions.defectFunctions as callMethod


@defectBluePrint.post('/createDefect')
@requireAction('create')
def createDefect():
    try:
        body = request.get_json() or {}
        
        projectId = body.get('projectId', '').strip()
        title = body.get('title', '').strip()
        description = body.get('description', '').strip()
        severity = body.get('severity', 'Media')
        priority = body.get('priority', 'Media')
        testCaseId = body.get('testCaseId', '')
        testExecutionId = body.get('testExecutionId', '')
        artifactId = body.get('artifactId', '')
        artifactName = body.get('artifactName', '')
        artifactVersion = body.get('artifactVersion', '')
        reportedBy = body.get('reportedBy', '').strip()
        assignedTo = body.get('assignedTo', '')
        stepsToReproduce = body.get('stepsToReproduce', '')
        environment = body.get('environment', '')
        
        if not projectId or not title or not reportedBy:
            return jsonify({**ResponseMessage.message422, "data": "projectId, title and reportedBy are required"}), 422
        
        result = callMethod.fnCreateDefect(
            projectId, title, description, severity, priority,
            testCaseId, testExecutionId, artifactId, artifactName,
            artifactVersion, reportedBy, assignedTo, stepsToReproduce, environment
        )
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@defectBluePrint.get('/getDefects/<projectId>')
def getDefectsByProject(projectId):
    try:
        result = callMethod.fnGetDefectsByProject(projectId)
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@defectBluePrint.get('/getDefect/<defectId>')
def getDefectById(defectId):
    try:
        result = callMethod.fnGetDefectById(defectId)
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@defectBluePrint.put('/updateDefect/<defectId>')
@requireAction('edit')
def updateDefect(defectId):
    try:
        body = request.get_json() or {}
        changedBy = body.pop('changedBy', 'unknown')
        
        if not body:
            return jsonify({**ResponseMessage.message422, "data": "No updates provided"}), 422
        
        result = callMethod.fnUpdateDefect(defectId, body, changedBy)
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@defectBluePrint.post('/addComment/<defectId>')
@requireAction('edit')
def addCommentToDefect(defectId):
    try:
        body = request.get_json() or {}
        
        author = body.get('author', '').strip()
        comment = body.get('comment', '').strip()
        
        if not author or not comment:
            return jsonify({**ResponseMessage.message422, "data": "author and comment are required"}), 422
        
        result = callMethod.fnAddCommentToDefect(defectId, author, comment)
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500
