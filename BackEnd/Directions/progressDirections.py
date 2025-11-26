from flask import Blueprint, jsonify, request

progressBluePrint = Blueprint('progressBluePrint', __name__, url_prefix='/api/progress')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

import BackEnd.Functions.progressFunctions as callMethod


@progressBluePrint.post('/postProgress')
def postProgress():
    try:
        body = request.get_json() or {}

        projectId = body.get('projectId', '').strip()
        iteration = body.get('iteration', '').strip()
        startDate = body.get('startDate', '')
        endDate = body.get('endDate', '')
        tasks = body.get('tasks', [])
        completionPercent = body.get('completionPercent', 0)
        blockers = body.get('blockers', '').strip()
        observations = body.get('observations', '').strip()

        if not all([projectId, iteration, startDate, endDate]):
            return ResponseMessage.message422

        objResult = callMethod.fnPostProgress(
            projectId=projectId,
            iteration=iteration,
            startDate=startDate,
            endDate=endDate,
            tasks=tasks,
            completionPercent=completionPercent,
            blockers=blockers,
            observations=observations
        )
        return jsonify(objResult)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@progressBluePrint.get('/getProgress/<projectId>')
def getProgress(projectId):
    try:
        objResult = callMethod.fnGetProgress(projectId)
        return jsonify(objResult)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@progressBluePrint.put('/updateProgress')
def updateProgress():
    try:
        body = request.get_json() or {}
        progressId = body.get('_id', '').strip()
        updates = body.get('updates', {})

        if not progressId or not updates:
            return ResponseMessage.message422

        objResult = callMethod.fnUpdateProgress(progressId, updates)
        return jsonify(objResult)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@progressBluePrint.get('/getSummary/<projectId>')
def getSummary(projectId):
    try:
        objResult = callMethod.fnGetSummary(projectId)
        return jsonify(objResult)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@progressBluePrint.get('/getHistory/<projectId>')
def getHistory(projectId):
    try:
        objResult = callMethod.fnGetHistory(projectId)
        return jsonify(objResult)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
