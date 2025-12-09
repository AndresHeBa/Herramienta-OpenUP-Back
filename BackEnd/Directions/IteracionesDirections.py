from flask import Blueprint, jsonify, request, logging

IteracionesBluePrint = Blueprint('IteracionesBluePrint', __name__, url_prefix='/api/iteracion')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.GlobalInfo.permissions import requireAction, requireAdmin

# Function import
import BackEnd.Functions.iteracionFuctions as callMethod


def _normalize_json_body():
    data = request.get_json(silent=True) or {}
    b64 = (data.get("strImageBase64") or "").strip()
    if b64:
        try:
            url = HelperFunctions.save_image_from_base64(b64)
            data["strImageUrl"] = url
            data.pop("strImageBase64", None)
        except ValueError as ve:
            return {"__error__": (422, str(ve))}
    return data


@IteracionesBluePrint.post('/postInteracion')
@requireAction('create')
def postIteracion():
    try:
        body = _normalize_json_body()

        if "__error__" in body:
            code, msg = body["__error__"]
            return jsonify({"status": code, "message": msg}), code

        # 🔹 Datos obligatorios
        projectIdentifier = body.get('projectIdentifier', '').strip()
        name = body.get('name', '').strip()
        startDate = body.get('startDate', '').strip()
        finallyDate = body.get('finallyDate', '').strip()
        phase = body.get('phase', '').strip()

        # 🔹 Opcionales
        goal = body.get('goal', '').strip()
        active = body.get('active', True)
        tasks = body.get('tasks', []) or []
        blockers = body.get('blockers', '').strip()
        observations = body.get('observations', '').strip()

        # ✅ Validación de campos obligatorios
        if not all([projectIdentifier, name, startDate, finallyDate, phase]):
            return ResponseMessage.message422

        # ✅ Llamar método de guardado
        objResult = callMethod.fnPostinteracion(
            id=projectIdentifier,
            name=name,
            startDate=startDate,
            finallyDate=finallyDate,
            goal=goal,
            phase=phase,
            active=active,
            tasks=tasks,
            blockers=blockers,
            observations=observations
        )

        return objResult

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

# READ - Obtener todas las iteraciones de un proyecto
@IteracionesBluePrint.get('/getIteraciones/<project_id>')
def getIteraciones(project_id):
    try:
        if not project_id or not project_id.strip():
            return ResponseMessage.message422

        objResult = callMethod.fnGetIterations(project_id.strip())
        
        return jsonify(objResult), objResult.get("status", 200)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# READ - Obtener una iteración específica
@IteracionesBluePrint.get('/getIteracion/<project_id>/<iteration_name>')
def getIteracion(project_id, iteration_name):
    try:
        if not project_id or not project_id.strip():
            return ResponseMessage.message422
        
        if not iteration_name or not iteration_name.strip():
            return ResponseMessage.message422

        objResult = callMethod.fnGetIteration(
            project_id.strip(), 
            iteration_name.strip()
        )
        
        return jsonify(objResult), objResult.get("status", 200)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# UPDATE - Actualizar una iteración
@IteracionesBluePrint.put('/putIteracion/<project_id>/<iteration_name>')
@requireAction('edit')
def putIteracion(project_id, iteration_name):
    try:
        body = _normalize_json_body()

        if "__error__" in body:
            code, msg = body["__error__"]
            return jsonify({"status": code, "message": msg}), code

        if not project_id or not project_id.strip():
            return ResponseMessage.message422
        
        if not iteration_name or not iteration_name.strip():
            return ResponseMessage.message422

        # 🔹 Obtener campos opcionales (solo actualiza lo que se envíe)
        startDate = body.get('startDate', '').strip() or None
        finallyDate = body.get('finallyDate', '').strip() or None
        goal = body.get('goal', '').strip() or None
        phase = body.get('phase', '').strip() or None
        active = body.get('active') if 'active' in body else None
        tasks = body.get('tasks') if 'tasks' in body else None
        blockers = body.get('blockers', '').strip() or None
        observations = body.get('observations', '').strip() or None

        # ✅ Llamar método de actualización
        objResult = callMethod.fnPutIteration(
            project_id=project_id.strip(),
            iteration_name=iteration_name.strip(),
            startDate=startDate,
            finallyDate=finallyDate,
            goal=goal,
            phase=phase,
            active=active,
            tasks=tasks,
            blockers=blockers,
            observations=observations
        )

        return objResult

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# UPDATE - Actualizar solo el progreso de tareas
@IteracionesBluePrint.patch('/updateProgress/<project_id>/<iteration_name>')
@requireAction('edit')
def updateProgress(project_id, iteration_name):
    try:
        body = request.get_json(silent=True) or {}

        if not project_id or not project_id.strip():
            return ResponseMessage.message422
        
        if not iteration_name or not iteration_name.strip():
            return ResponseMessage.message422

        tasks = body.get('tasks')
        
        if not tasks or not isinstance(tasks, list):
            return ResponseMessage.message422

        # ✅ Llamar método de actualización de progreso
        objResult = callMethod.fnUpdateIterationProgress(
            project_id=project_id.strip(),
            iteration_name=iteration_name.strip(),
            tasks=tasks
        )

        return objResult

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# DELETE - Eliminar una iteración
@IteracionesBluePrint.delete('/deleteIteracion/<project_id>/<iteration_name>')
@requireAdmin
def deleteIteracion(project_id, iteration_name):
    try:
        if not project_id or not project_id.strip():
            return ResponseMessage.message422
        
        if not iteration_name or not iteration_name.strip():
            return ResponseMessage.message422

        # ✅ Llamar método de eliminación
        objResult = callMethod.fnDeleteIteration(
            project_id=project_id.strip(),
            iteration_name=iteration_name.strip()
        )

        return objResult

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500