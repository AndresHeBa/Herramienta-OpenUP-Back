from flask import Blueprint, jsonify, request

planBluePrint = Blueprint('planBluePrint', __name__, url_prefix='/api/plan')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

# Functions import
import BackEnd.Functions.planFunctions as callMethod


@planBluePrint.post('/postPlan')
def postPlan():
    try:
        body = request.get_json() or {}

        projectId = body.get('projectId', '').strip()
        objectives = body.get('objectives', '').strip()
        scope = body.get('scope', '').strip()
        initialSchedule = body.get('initialSchedule', {})
        phaseResponsibles = body.get('phaseResponsibles', {})
        milestones = body.get('milestones', [])
        observations = body.get('observations', '').strip()
        version = body.get('version', '1')

        # Validar campos requeridos
        if not all([projectId, objectives, scope, initialSchedule]):
            return ResponseMessage.message422

        # Llamar función para crear el plan
        objResult = callMethod.fnPostPlan(
            projectId=projectId,
            objectives=objectives,
            scope=scope,
            initialSchedule=initialSchedule,
            phaseResponsibles=phaseResponsibles,
            milestones=milestones,
            observations=observations,
            version=version
        )
        return jsonify(objResult)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@planBluePrint.get('/getPlan/<projectId>')
def getPlan(projectId):
    try:
        objResult = callMethod.fnGetPlan(projectId)
        return jsonify(objResult)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@planBluePrint.put('/updatePlan')
def updatePlan():
    try:
        body = request.get_json() or {}
        planId = body.get('_id', '').strip()
        updates = body.get('updates', {})

        if not planId or not updates:
            return ResponseMessage.message422

        objResult = callMethod.fnUpdatePlan(planId, updates)
        return jsonify(objResult)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
