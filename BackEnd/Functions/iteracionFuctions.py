from datetime import datetime
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

from bson.objectid import ObjectId

dbConnLocal = HelperFunctions.dbConnection()

def fnPostinteracion(id, name, startDate, finallyDate, goal, phase, active, tasks=None, blockers="", observations=""):
    try:

        if tasks is None:
            tasks = []

        completed_tasks = sum(1 for t in tasks if t.get("completed") == True)
        total_tasks = len(tasks)

        completion_percent = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0

        # Verificar si ya existe una iteración con el mismo nombre para este proyecto
        existing = dbConnLocal.clProgress.find_one({
            "projectId": str(id),
            "iteration": name
        })
        
        if existing:
            return ResponseMessage.message409

        iteracion = {
            "projectId": str(id),
            "iteration": name,
            "startDate": startDate,
            "endDate": finallyDate,
            "tasks": tasks,
            "completionPercent": completion_percent,
            "goal": goal,
            "phase": phase,
            "blockers": blockers,
            "observations": observations,
            "creationDate": datetime.utcnow(),
            "version": 1,
            "status": "Active" if active else "Inactive",
            "active": active
        }

        iteracion = HelperFunctions.deleteBlankAttributes(iteracion)

        # Insertar en la colección clProgress
        result = dbConnLocal.clProgress.insert_one(iteracion)

        if not result.inserted_id:
            return ResponseMessage.message500

        return ResponseMessage.message201

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

# READ - Obtener todas las iteraciones de un proyecto
def fnGetIterations(project_id):
    try:
        print(f"🔍 Buscando iteraciones para projectId: {project_id}")
        
        # Buscar iteraciones en la colección clProgress filtradas por projectId
        iterations = list(dbConnLocal.clProgress.find({"projectId": project_id}))
        
        print(f"📊 Iteraciones encontradas: {len(iterations)}")
        
        # Convertir ObjectId a string para serialización
        for iteration in iterations:
            if "_id" in iteration:
                iteration["_id"] = str(iteration["_id"])

        return {
            "status": 200,
            "data": iterations,
            "message": "Iterations retrieved successfully"
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# READ - Obtener una iteración específica
def fnGetIteration(project_id, iteration_name):
    try:
        iteration = dbConnLocal.clProgress.find_one({
            "projectId": project_id,
            "iteration": iteration_name
        })

        if not iteration:
            return ResponseMessage.message404
        
        if "_id" in iteration:
            iteration["_id"] = str(iteration["_id"])

        return {
            "status": 200,
            "data": iteration,
            "message": "Iteration retrieved successfully"
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# UPDATE - Actualizar una iteración
def fnPutIteration(project_id, iteration_name, startDate=None, finallyDate=None, goal=None, 
                   phase=None, active=None, tasks=None, blockers=None, observations=None):
    try:
        # Construir el objeto de actualización solo con campos proporcionados
        update_fields = {}
        
        if startDate is not None:
            update_fields["startDate"] = startDate
        if finallyDate is not None:
            update_fields["endDate"] = finallyDate
        if goal is not None:
            update_fields["goal"] = goal
        if phase is not None:
            update_fields["phase"] = phase
        if active is not None:
            update_fields["status"] = "Active" if active else "Inactive"
            update_fields["active"] = active
        if tasks is not None:
            completed_tasks = sum(1 for t in tasks if t.get("completed") == True)
            total_tasks = len(tasks)
            completion_percent = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0
            
            update_fields["tasks"] = tasks
            update_fields["completionPercent"] = completion_percent
        if blockers is not None:
            update_fields["blockers"] = blockers
        if observations is not None:
            update_fields["observations"] = observations

        if not update_fields:
            return {
                "status": 400,
                "message": "No fields to update"
            }

        result = dbConnLocal.clProgress.update_one(
            {
                "projectId": project_id,
                "iteration": iteration_name
            },
            {
                "$set": update_fields,
                "$inc": {"version": 1}
            }
        )

        if result.matched_count == 0:
            return ResponseMessage.message404
        
        if result.modified_count == 0:
            return {
                "status": 304,
                "message": "No changes made"
            }

        return ResponseMessage.message200

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# DELETE - Eliminar una iteración
def fnDeleteIteration(project_id, iteration_name):
    try:
        result = dbConnLocal.clProgress.delete_one({
            "projectId": project_id,
            "iteration": iteration_name
        })

        if result.deleted_count == 0:
            return ResponseMessage.message404

        return ResponseMessage.message200

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# BONUS - Actualizar solo el progreso de tareas
def fnUpdateIterationProgress(project_id, iteration_name, tasks):
    try:
        completed_tasks = sum(1 for t in tasks if t.get("completed") == True)
        total_tasks = len(tasks)
        completion_percent = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0

        result = dbConnLocal.clProgress.update_one(
            {
                "projectId": project_id,
                "iteration": iteration_name
            },
            {
                "$set": {
                    "tasks": tasks,
                    "completionPercent": completion_percent
                },
                "$inc": {"version": 1}
            }
        )

        if result.matched_count == 0:
            return ResponseMessage.message404

        return ResponseMessage.message200

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500