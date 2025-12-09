import os
from datetime import datetime
from bson import ObjectId
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.Functions.configurationFunctions as ConfigFunctions

dbConnLocal = HelperFunctions.dbConnection()

BASE_UPLOAD_FOLDER = "BackEnd/Uploads"

# Required artifacts per phase (HU-006..HU-009). Keys are normalized to lowercase.
REQUIRED_ARTIFACTS = {
    "inception": [
        {"type": "Documento de Visión", "mandatory": True},
        {"type": "Lista de Stakeholders", "mandatory": True},
        {"type": "Lista de Riesgos Iniciales", "mandatory": True},
        {"type": "Plan de Proyecto", "mandatory": True},
        {"type": "Modelo de Casos de Uso de Alto Nivel", "mandatory": True}
    ],
    "elaboration": [
        {"type": "Modelo de Casos de Uso Detallado", "mandatory": True},
        {"type": "Modelo de Dominio", "mandatory": True},
        {"type": "Especificación Requerimientos Supl.", "mandatory": True},
        {"type": "No Funcionales", "mandatory": False},
        {"type": "Documento de Arquitectura", "mandatory": True},
        {"type": "Diagramas Técnicos", "mandatory": False},
        {"type": "Plan de Iteraciones", "mandatory": True},
        {"type": "Prototipo de UI", "mandatory": False}
    ],
    "construction": [
        {"type": "Modelo de Diseño Detallado", "mandatory": True},
        {"type": "Código Fuente", "mandatory": False},
        {"type": "Casos de Prueba", "mandatory": True},
        {"type": "Resultados de Pruebas", "mandatory": False},
        {"type": "Registro de Iteraciones", "mandatory": True}
    ],
    "transition": [
        {"type": "Manual de Usuario", "mandatory": True},
        {"type": "Manual Técnico", "mandatory": True},
        {"type": "Plan de Despliegue", "mandatory": True},
        {"type": "Documento de Cierre", "mandatory": True},
        {"type": "Build Final", "mandatory": True},
        {"type": "Reporte de Pruebas Beta", "mandatory": False}
    ]
}


def fnUploadArtifact(file, filename, projectId, phase, artifactType,
                     author, date, isMandatory, prototypeLink, tags,
                     content=None, externalLink=None, testEntries=None, observations=None):
    try:
        # Buscar última versión del artefacto por tipo y fase
        lastVersion = dbConnLocal.clArtifacts.find_one(
            {"projectId": projectId, "artifactType": artifactType, "phase": phase},
            sort=[("version", -1)]
        )
        newVersion = int(lastVersion["version"]) + 1 if lastVersion else 1

        # Si hay archivo físico, guardarlo
        filePath = None
        if file:
            extension = filename.rsplit('.', 1)[-1].lower()
            folder_path = os.path.join(BASE_UPLOAD_FOLDER, projectId, phase, artifactType, f"v{newVersion}")
            os.makedirs(folder_path, exist_ok=True)
            filePath = os.path.join(folder_path, filename)
            file.save(filePath)

        # Registro final
        # Si ya existe una versión previa y se está creando una nueva versión,
        # el criterio de aceptación exige una descripción de cambios (observaciones).
        if lastVersion and (newVersion > int(lastVersion.get("version", 0))):
            if not observations or observations.strip() == "":
                return {**ResponseMessage.message422, "data": "observations required when creating a new version"}

        artifact = {
            "projectId": projectId,
            "phase": phase,
            "artifactType": artifactType,
            "filename": filename,
            "filePath": filePath,
            "version": newVersion,
            "content": content,
            "observations": observations,
            "fileType": filename.rsplit('.', 1)[-1].lower() if filename else None,
            "isDiagram": filename.endswith(('png', 'jpg', 'jpeg', 'svg', 'pdf')) and 'diagrama' in artifactType.lower(),
            "prototypeLink": prototypeLink,
            "externalLink": externalLink,
            "testEntries": testEntries,
            "author": author,
            # registro de fecha de entrega: si viene, usarla; si no, usar ahora
            "uploadDate": date if date else datetime.now().isoformat(),
            "isMandatory": isMandatory,
            "status": "Pendiente",
            "tags": tags,
            "createdAt": datetime.now()
        }

        dbConnLocal.clArtifacts.insert_one(artifact)

        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=author or 'system',
            action_type='create',
            entity_type='artifact',
            entity_id=str(artifact['_id']),
            details={
                'artifactType': artifactType,
                'phase': phase,
                'version': newVersion,
                'filename': filename,
                'observations': observations
            },
            project_id=projectId
        )

        return {
            **ResponseMessage.message200,
            "message": f"Artifact uploaded successfully - Version {newVersion}",
            "version": newVersion
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



def fnGetArtifacts(projectId, phase=None):
    try:
        # Si se pide por fase y la fase está en el mapeo de requeridos, devolver el catálogo de artefactos requeridos y su estado
        if phase:
            key = phase.strip().lower()
            required = REQUIRED_ARTIFACTS.get(key)
            if required:
                response_list = []
                for req in required:
                    art_type = req["type"]
                    latest = dbConnLocal.clArtifacts.find_one({
                        "projectId": projectId,
                        "artifactType": art_type,
                        "phase": phase
                    }, sort=[("version", -1)])

                    item = {
                        "artifactType": art_type,
                        "mandatory": req.get("mandatory", False),
                        "status": latest.get("status") if latest else "No entregado",
                        "version": latest.get("version") if latest else None,
                        "filename": latest.get("filename") if latest else None,
                        "filePath": latest.get("filePath") if latest else None,
                        "uploadDate": latest.get("uploadDate") if latest else None,
                        "author": latest.get("author") if latest else None,
                        "tags": latest.get("tags") if latest else []
                    }
                    response_list.append(item)

                return {**ResponseMessage.message200, "Result": response_list}

            # si la fase no está en el mapeo, retornamos los artefactos almacenados para esa fase
            results = list(dbConnLocal.clArtifacts.find({"projectId": projectId, "phase": phase}))
        else:
            results = list(dbConnLocal.clArtifacts.find({"projectId": projectId}))

        for res in results:
            res["_id"] = str(res["_id"])

        return {**ResponseMessage.message200, "Result": results}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
    
def fnGetArtifactHistory(projectId, artifactType):
    try:
        records = list(dbConnLocal.clArtifacts.find(
            {"projectId": projectId, "artifactType": artifactType}
        ).sort("version", -1))

        for r in records:
            r["_id"] = str(r["_id"])

        # provide a simple metadata-only view too
        metadata_only = []
        for r in records:
            metadata_only.append({
                "version": r.get("version"),
                "author": r.get("author"),
                "uploadDate": r.get("uploadDate"),
                "filename": r.get("filename"),
                "fileType": r.get("fileType"),
                "isMandatory": r.get("isMandatory"),
                "status": r.get("status"),
                "observations": r.get("observations"),
                "tags": r.get("tags", [])
            })

        return {**ResponseMessage.message200, "Result": records, "Metadata": metadata_only}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



def fnRestoreArtifactVersion(artifactId, versionToRestore):
    try:
        artifact = dbConnLocal.clArtifacts.find_one({"_id": ObjectId(artifactId)})
        if not artifact:
            return ResponseMessage.message404

        restored = dbConnLocal.clArtifacts.find_one({
            "projectId": artifact["projectId"],
            "artifactType": artifact["artifactType"],
            "version": int(versionToRestore)
        })

        if not restored:
            return {**ResponseMessage.message404, "data": "Version not found"}

        # Crear nueva versión a partir de la restaurada
        newVersion = dbConnLocal.clArtifacts.find_one(
            {"projectId": artifact["projectId"], "artifactType": artifact["artifactType"]},
            sort=[("version", -1)]
        )["version"] + 1

        restored["_id"] = ObjectId()
        restored["version"] = newVersion
        restored["createdAt"] = datetime.now()
        restored["status"] = "Pendiente"

        dbConnLocal.clArtifacts.insert_one(restored)

        return {
            **ResponseMessage.message200,
            "message": f"Version restored as version {newVersion}",
            "version": newVersion
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnCompareArtifactVersions(projectId, artifactType, v1, v2):
    try:
        one = dbConnLocal.clArtifacts.find_one({
            "projectId": projectId,
            "artifactType": artifactType,
            "version": int(v1)
        })
        two = dbConnLocal.clArtifacts.find_one({
            "projectId": projectId,
            "artifactType": artifactType,
            "version": int(v2)
        })

        if not one or not two:
            return {**ResponseMessage.message404, "data": "One or both versions not found"}

        # Campos a comparar (metadatos)
        keys = ["version", "author", "uploadDate", "filename", "fileType", "isMandatory", "status", "observations", "tags", "externalLink", "prototypeLink"]
        diff = {"v1": {}, "v2": {}, "differences": {}}
        for k in keys:
            v_one = one.get(k)
            v_two = two.get(k)
            diff["v1"][k] = v_one
            diff["v2"][k] = v_two
            if v_one != v_two:
                diff["differences"][k] = {"v1": v_one, "v2": v_two}

        return {**ResponseMessage.message200, "Result": diff}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateMandatoryStatus(updateList):
    """
    HU-011: Update mandatory/optional status for a list of artifact types.
    This updates all artifacts with the specified types across all projects and phases.
    """
    try:
        updated_count = 0
        errors = []

        for item in updateList:
            artifactType = item.get('artifactType')
            isMandatory = item.get('isMandatory')
            # Validate that the artifact type exists
            existing = dbConnLocal.clArtifactTypes.find_one({
                "artifactType": artifactType
            })

            if not existing:
                errors.append(f"Artifact type not found: {artifactType}")
                continue

            # Update all artifacts with this type across all projects and phases
            result = dbConnLocal.clArtifactTypes.update_many(
                {
                    "artifactType": artifactType
                },
                {
                    "$set": {
                        "isMandatory": isMandatory,
                        "updatedAt": datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                updated_count += 1

            # Also update the REQUIRED_ARTIFACTS dictionary for all phases
            for phase_key in REQUIRED_ARTIFACTS:
                for artifact in REQUIRED_ARTIFACTS[phase_key]:
                    if artifact["type"] == artifactType:
                        artifact["mandatory"] = isMandatory

        return {
            **ResponseMessage.message200,
            "message": "Bulk update processed",
            "updatedTypesCount": updated_count,
            "errors": errors
        }

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetArtifactTypes():
    try:
        # Use adapter to read from active configuration
        results = ConfigFunctions.fnGetArtifactTypesFromActiveConfig()
        
        for res in results:
            if "_id" in res:
                res["_id"] = str(res["_id"])
            
        return {**ResponseMessage.message200, "Result": results}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetMandatoryArtifactTypes():
    try:
        # Use adapter and filter mandatory
        all_artifacts = ConfigFunctions.fnGetArtifactTypesFromActiveConfig()
        results = [a for a in all_artifacts if a.get("isMandatory", False)]
        
        for res in results:
            if "_id" in res:
                res["_id"] = str(res["_id"])
            
        return {**ResponseMessage.message200, "Result": results}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateArtifactState(artifactId, workflowId=None, state=None, assignedTo=None, userId=None, comments=None):
    """
    HU-012: Update artifact workflow state and/or assign workflow.
    Can be used to:
    1. Assign a workflow to an artifact (provide workflowId + initial state)
    2. Update state within existing workflow (provide state only)
    3. Update both workflow and state
    """
    try:
        if not artifactId:
            return ResponseMessage.message422

        if not ObjectId.is_valid(artifactId):
            return {**ResponseMessage.message422, "data": "Invalid artifactId"}

        # Verify artifact exists
        artifact = dbConnLocal.clArtifacts.find_one({"_id": ObjectId(artifactId)})
        if not artifact:
            return {**ResponseMessage.message404, "data": "Artifact not found"}

        update_fields = {"updatedAt": datetime.now()}
        history_entry = {
            "artifactId": artifactId,
            "userId": userId,
            "comments": comments,
            "timestamp": datetime.now()
        }

        # If workflowId is provided, assign or update workflow
        if workflowId:
            if not ObjectId.is_valid(workflowId):
                return {**ResponseMessage.message422, "data": "Invalid workflowId"}
            
            workflow = dbConnLocal.clWorkflows.find_one({"_id": ObjectId(workflowId), "isActive": True})
            if not workflow:
                return {**ResponseMessage.message404, "data": "Workflow not found or inactive"}

            previous_workflow = artifact.get("currentWorkflowId") or artifact.get("workflowId")
            update_fields["currentWorkflowId"] = workflowId
            update_fields["workflowName"] = workflow.get("name")
            history_entry["previousWorkflowId"] = previous_workflow
            history_entry["newWorkflowId"] = workflowId

        # If state is provided, update state
        if state:
            previous_state = artifact.get("currentState") or artifact.get("status")
            update_fields["currentState"] = state
            update_fields["status"] = state  # Keep both for backward compatibility
            history_entry["previousState"] = previous_state
            history_entry["newState"] = state

        # If assignedTo is provided, update assignment
        if assignedTo is not None:
            update_fields["assignedTo"] = assignedTo
            history_entry["assignedTo"] = assignedTo

        # Record history only if there are actual changes
        if "previousState" in history_entry or "previousWorkflowId" in history_entry:
            dbConnLocal.clArtifactStateHistory.insert_one(history_entry)

        # Update artifact
        dbConnLocal.clArtifacts.update_one(
            {"_id": ObjectId(artifactId)},
            {"$set": update_fields}
        )

        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=userId or 'system',
            action_type='status_change',
            entity_type='artifact',
            entity_id=artifactId,
            details={
                'previousState': history_entry.get('previousState'),
                'newState': history_entry.get('newState'),
                'workflowId': workflowId,
                'assignedTo': assignedTo,
                'comments': comments
            },
            project_id=artifact.get('projectId')
        )

        return {**ResponseMessage.message200, "message": "Artifact state updated successfully"}

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnReassignArtifactPhase(artifact_id, new_phase, user_id, reason=None):
    """
    Reasignar un artefacto a una nueva fase (HU-020)
    - Conserva el historial de versiones y estados
    - Registra el movimiento con usuario y fecha
    - Valida reglas de negocio antes de mover
    """
    try:
        if not ObjectId.is_valid(artifact_id):
            return {**ResponseMessage.message422, "message": "Invalid artifact ID"}
        
        # Get the artifact
        artifact = dbConnLocal.clArtifacts.find_one({"_id": ObjectId(artifact_id)})
        
        if not artifact:
            return ResponseMessage.message404
        
        old_phase = artifact.get("phase")
        project_id = artifact.get("projectId")
        artifact_type = artifact.get("artifactType")
        
        # Validate if phase is actually changing
        if old_phase == new_phase:
            return {**ResponseMessage.message422, "message": "Artifact is already in this phase"}
        
        # Check for mandatory artifacts violations (e.g., moving to Transition without required artifacts)
        validation_result = _validate_phase_reassignment(project_id, old_phase, new_phase, artifact_type)
        
        if not validation_result["allowed"]:
            return {
                **ResponseMessage.message422,
                "message": validation_result["message"],
                "requiresConfirmation": True,
                "warnings": validation_result.get("warnings", [])
            }
        
        # Create movement record
        movement_record = {
            "artifactId": str(artifact_id),
            "projectId": project_id,
            "artifactType": artifact_type,
            "oldPhase": old_phase,
            "newPhase": new_phase,
            "movedBy": user_id,
            "movedAt": datetime.now(),
            "reason": reason or "Phase reassignment",
            "version": artifact.get("version")
        }
        
        dbConnLocal.clArtifactMovements.insert_one(movement_record)
        
        # Update artifact phase (preserve all history)
        dbConnLocal.clArtifacts.update_one(
            {"_id": ObjectId(artifact_id)},
            {
                "$set": {
                    "phase": new_phase,
                    "lastModifiedBy": user_id,
                    "lastModifiedAt": datetime.now()
                }
            }
        )
        
        print(f"✅ Artifact {artifact_type} moved from {old_phase} to {new_phase} by {user_id}")
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=user_id,
            action_type='move',
            entity_type='artifact',
            entity_id=str(artifact_id),
            details={
                'oldPhase': old_phase,
                'newPhase': new_phase,
                'reason': reason,
                'artifactType': artifact.get('artifactType')
            },
            project_id=project_id
        )
        
        return {
            **ResponseMessage.message200,
            "message": f"Artifact successfully moved from {old_phase} to {new_phase}",
            "data": {
                "artifactId": str(artifact_id),
                "oldPhase": old_phase,
                "newPhase": new_phase,
                "movedAt": movement_record["movedAt"].isoformat()
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def _validate_phase_reassignment(project_id, old_phase, new_phase, artifact_type):
    """
    Validate if artifact can be moved to new phase
    Returns dict with 'allowed' (bool), 'message' (str), and optional 'warnings' (list)
    """
    warnings = []
    
    # Check if moving to Transition phase
    if new_phase.lower() in ['transición', 'transition']:
        # Get all mandatory artifacts for previous phases
        mandatory_check = _check_mandatory_artifacts_completion(project_id)
        
        if not mandatory_check["complete"]:
            return {
                "allowed": False,
                "message": f"Cannot move to Transition: Missing mandatory artifacts - {', '.join(mandatory_check['missing'])}",
                "warnings": mandatory_check.get("missing", [])
            }
    
    # Check if moving backwards (e.g., from Construction to Elaboration)
    phase_order = {
        'incepción': 1, 'inception': 1,
        'elaboración': 2, 'elaboration': 2,
        'construcción': 3, 'construction': 3,
        'transición': 4, 'transition': 4
    }
    
    old_order = phase_order.get(old_phase.lower(), 0)
    new_order = phase_order.get(new_phase.lower(), 0)
    
    if new_order < old_order:
        warnings.append(f"Moving backwards from {old_phase} to {new_phase}")
    
    return {
        "allowed": True,
        "message": "Reassignment allowed",
        "warnings": warnings
    }


def _check_mandatory_artifacts_completion(project_id):
    """Check if all mandatory artifacts are uploaded for a project"""
    missing = []
    
    # Get all artifacts for the project
    artifacts = list(dbConnLocal.clArtifacts.find({"projectId": project_id}))
    
    # Check each phase's mandatory artifacts
    for phase_key, required_list in REQUIRED_ARTIFACTS.items():
        for req in required_list:
            if req.get("mandatory"):
                artifact_type = req["type"]
                # Check if this artifact type exists for the project
                exists = any(a.get("artifactType") == artifact_type for a in artifacts)
                if not exists:
                    missing.append(f"{artifact_type} ({phase_key})")
    
    return {
        "complete": len(missing) == 0,
        "missing": missing
    }


def fnGetArtifactMovementHistory(artifact_id):
    """Get movement history for a specific artifact"""
    try:
        if not ObjectId.is_valid(artifact_id):
            return {**ResponseMessage.message422, "message": "Invalid artifact ID"}
        
        movements = list(dbConnLocal.clArtifactMovements.find(
            {"artifactId": artifact_id}
        ).sort("movedAt", -1))
        
        for mov in movements:
            mov["_id"] = str(mov["_id"])
            if isinstance(mov.get("movedAt"), datetime):
                mov["movedAt"] = mov["movedAt"].isoformat()
        
        return {
            **ResponseMessage.message200,
            "data": movements
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
