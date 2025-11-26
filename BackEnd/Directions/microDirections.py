from flask import Blueprint, jsonify, request

microBluePrint = Blueprint('microBluePrint', __name__, url_prefix='/api/microincrement')

import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.Functions.microFunctions as callMethod


@microBluePrint.post('/postMicroincrement')
def postMicroincrement():
    try:
        body = request.json or {}

        objResult = callMethod.fnPostMicroincrement(
            projectId=body.get("projectId", "").strip(),
            iteration=body.get("iteration", "").strip(),
            deliverable=body.get("deliverable", "").strip(),
            title=body.get("title", "").strip(),
            description=body.get("description", "").strip(),
            date=body.get("date", "").strip(),
            author=body.get("author", "").strip()
        )

        return jsonify(objResult)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



@microBluePrint.get('/getMicroincrement/<microId>')
def getMicroincrement(microId):
    try:
        objResult = callMethod.fnGetMicroincrement(microId)
        return jsonify(objResult)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



@microBluePrint.get('/getMicroincrementList')
def getMicroincrementList():
    try:
        projectId = request.args.get("projectId")
        iteration = request.args.get("iteration")
        deliverable = request.args.get("deliverable")
        author = request.args.get("author")

        objResult = callMethod.fnGetMicroincrementList(projectId, iteration, deliverable, author)
        return jsonify(objResult)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
