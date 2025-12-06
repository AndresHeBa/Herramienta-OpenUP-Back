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

        iteracion = {
            "_id": ObjectId(),
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
            "status": "Active" if active else "Inactive"
        }

        iteracion = HelperFunctions.deleteBlankAttributes(iteracion)

        
        result = dbConnLocal.clProjects.update_one(
            {
                "_id": ObjectId(id),
                "iterations.iteration": {"$ne": name}  # evita duplicados
            },
            {
                "$push": {"iterations": iteracion}
            }
        )

        if result.modified_count == 0:
            return ResponseMessage.message409

        return ResponseMessage.message201

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500

# READ - Obtener todas las iteraciones de un proyecto
def fnGetIterations(project_id):
    try:
        project = dbConnLocal.clProjects.find_one(
            {"_id": ObjectId(project_id)},
            {"iterations": 1, "_id": 0}
        )

        if not project:
            return ResponseMessage.message404

        iterations = project.get("iterations", [])
        
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
        project = dbConnLocal.clProjects.find_one(
            {"_id": ObjectId(project_id)},
            {"iterations": {"$elemMatch": {"iteration": iteration_name}}}
        )

        if not project or "iterations" not in project or len(project["iterations"]) == 0:
            return ResponseMessage.message404

        iteration = project["iterations"][0]
        
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
            update_fields["iterations.$.startDate"] = startDate
        if finallyDate is not None:
            update_fields["iterations.$.endDate"] = finallyDate
        if goal is not None:
            update_fields["iterations.$.goal"] = goal
        if phase is not None:
            update_fields["iterations.$.phase"] = phase
        if active is not None:
            update_fields["iterations.$.status"] = "Active" if active else "Inactive"
        if tasks is not None:
            completed_tasks = sum(1 for t in tasks if t.get("completed") == True)
            total_tasks = len(tasks)
            completion_percent = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0
            
            update_fields["iterations.$.tasks"] = tasks
            update_fields["iterations.$.completionPercent"] = completion_percent
        if blockers is not None:
            update_fields["iterations.$.blockers"] = blockers
        if observations is not None:
            update_fields["iterations.$.observations"] = observations

        if not update_fields:
            return {
                "status": 400,
                "message": "No fields to update"
            }

        # Incrementar versión
        update_fields["iterations.$.version"] = {"$inc": 1}

        result = dbConnLocal.clProjects.update_one(
            {
                "_id": ObjectId(project_id),
                "iterations.iteration": iteration_name
            },
            {
                "$set": update_fields
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
        result = dbConnLocal.clProjects.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$pull": {
                    "iterations": {"iteration": iteration_name}
                }
            }
        )

        if result.matched_count == 0:
            return ResponseMessage.message404

        if result.modified_count == 0:
            return {
                "status": 404,
                "message": "Iteration not found in project"
            }

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

        result = dbConnLocal.clProjects.update_one(
            {
                "_id": ObjectId(project_id),
                "iterations.iteration": iteration_name
            },
            {
                "$set": {
                    "iterations.$.tasks": tasks,
                    "iterations.$.completionPercent": completion_percent
                },
                "$inc": {
                    "iterations.$.version": 1
                }
            }
        )

        if result.matched_count == 0:
            return ResponseMessage.message404

        return ResponseMessage.message200

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500