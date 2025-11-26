import os
from datetime import datetime
from bson import ObjectId
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

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

