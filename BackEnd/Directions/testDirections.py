from flask import Blueprint, jsonify, request

testBluePrint = Blueprint('testBluePrint', __name__, url_prefix='/api/test')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.GlobalInfo.permissions import requireAction

import BackEnd.Functions.testFunctions as callMethod


@testBluePrint.post('/createTestCase')
@requireAction('create')
def createTestCase():
    try:
        body = request.get_json() or {}
        
        projectId = body.get('projectId', '').strip()
        name = body.get('name', '').strip()
        description = body.get('description', '').strip()
        artifactId = body.get('artifactId', '').strip()
        artifactName = body.get('artifactName', '').strip()
        preconditions = body.get('preconditions', '').strip()
        steps = body.get('steps', [])
        expectedResult = body.get('expectedResult', '').strip()
        priority = body.get('priority', 'Media')
        createdBy = body.get('createdBy', '').strip()
        
        if not projectId or not name:
            return jsonify({**ResponseMessage.message422, "data": "projectId and name are required"}), 422
        
        result = callMethod.fnCreateTestCase(
            projectId, name, description, artifactId, artifactName,
            preconditions, steps, expectedResult, priority, createdBy
        )
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@testBluePrint.get('/getTestCases/<projectId>')
def getTestCasesByProject(projectId):
    try:
        result = callMethod.fnGetTestCasesByProject(projectId)
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@testBluePrint.post('/executeTestCase')
@requireAction('edit')
def executeTestCase():
    try:
        body = request.get_json() or {}
        
        testCaseId = body.get('testCaseId', '').strip()
        projectId = body.get('projectId', '').strip()
        executedBy = body.get('executedBy', '').strip()
        status = body.get('status', 'No Ejecutado')
        actualResult = body.get('actualResult', '')
        evidence = body.get('evidence', '')
        notes = body.get('notes', '')
        iteration = body.get('iteration', '')
        
        if not testCaseId or not projectId or not executedBy:
            return jsonify({**ResponseMessage.message422, "data": "testCaseId, projectId and executedBy are required"}), 422
        
        result = callMethod.fnExecuteTestCase(
            testCaseId, projectId, executedBy, status,
            actualResult, evidence, notes, iteration
        )
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@testBluePrint.get('/getExecutions/<projectId>')
def getTestExecutionsByProject(projectId):
    try:
        result = callMethod.fnGetTestExecutionsByProject(projectId)
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@testBluePrint.get('/getExecutions/testCase/<testCaseId>')
def getTestExecutionsByTestCase(testCaseId):
    try:
        result = callMethod.fnGetTestExecutionsByTestCase(testCaseId)
        
        if result.get('intCode') == 200:
            return jsonify(result)
        
        return jsonify(result), result.get('intCode', 500)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500
