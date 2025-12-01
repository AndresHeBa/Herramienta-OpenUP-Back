from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.Functions.artifactFunctions as callMethod

artifactBluePrint = Blueprint('artifactBluePrint', __name__, url_prefix='/api/artifacts')


@artifactBluePrint.post('/uploadArtifact')
def uploadArtifact():
    try:
        file = request.files.get('file')
        projectId = request.form.get('projectId', '').strip()
        phase = request.form.get('phase', '').strip()   # Inception, Elaboration...
        artifactType = request.form.get('artifactType', '').strip()
        author = request.form.get('author', '').strip()
        date = request.form.get('date', '').strip()
        content = request.form.get('content', '').strip()
        externalLink = request.form.get('externalLink', '').strip()
        # testEntries can be sent as JSON string or omitted
        testEntries = request.form.get('testEntries')
        tags = request.form.getlist('tags')
        isMandatory = request.form.get('isMandatory', 'false').strip().lower() == 'true'
        prototypeLink = request.form.get('prototypeLink', '').strip()

        # Validar campos requeridos
        if not all([projectId, phase, artifactType, author, date]):
            return ResponseMessage.message422

        # Validar archivos o enlaces para prototipo
        if not file and not prototypeLink:
            return {**ResponseMessage.message422, "data": "No file or link provided"}

        filename = secure_filename(file.filename) if file else None

        result = callMethod.fnUploadArtifact(
            file=file,
            filename=filename,
            projectId=projectId,
            phase=phase,
            artifactType=artifactType,
            author=author,
            date=date,
            isMandatory=isMandatory,
            prototypeLink=prototypeLink,
            tags=tags,
            content=content,
            externalLink=externalLink,
            testEntries=testEntries,
            observations=request.form.get('observations', '').strip()
        )

        print("Artifact uploaded:", result)
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500



@artifactBluePrint.get('/getArtifacts')
def getArtifactList():
    try:
        projectId = request.args.get('projectId')
        phase = request.args.get('phase')
        
        print("Received projectId:", projectId)
        print("Received phase:", phase)

        if not projectId:
            return {**ResponseMessage.message422, "data": "projectId is required"}

        result = callMethod.fnGetArtifacts(projectId, phase)
        # print("Artifacts fetched:", result)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@artifactBluePrint.get('/history/<projectId>/<artifactType>')
def getArtifactHistory(projectId, artifactType):
    try:
        # If query param download=true, return as attachment (JSON)
        result = callMethod.fnGetArtifactHistory(projectId, artifactType)
        download = request.args.get('download', '').lower() in ['1', 'true', 'yes']
        if download and result.get('Result') is not None:
            from flask import Response
            import json
            payload = json.dumps(result['Result'], default=str, ensure_ascii=False)
            resp = Response(payload, mimetype='application/json')
            resp.headers['Content-Disposition'] = f'attachment; filename="{projectId}_{artifactType}_history.json"'
            return resp
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@artifactBluePrint.put('/restoreVersion')
def restoreArtifactVersion():
    try:
        body = request.get_json() or {}
        artifactId = body.get('artifactId', '').strip()
        versionToRestore = body.get('version', '').strip()

        if not artifactId or not versionToRestore:
            return ResponseMessage.message422

        result = callMethod.fnRestoreArtifactVersion(artifactId, versionToRestore)
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@artifactBluePrint.get('/compare')
def compareArtifactVersions():
    try:
        projectId = request.args.get('projectId')
        artifactType = request.args.get('artifactType')
        v1 = request.args.get('v1')
        v2 = request.args.get('v2')

        if not all([projectId, artifactType, v1, v2]):
            return ResponseMessage.message422

        result = callMethod.fnCompareArtifactVersions(projectId, artifactType, v1, v2)
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@artifactBluePrint.put('/updateMandatoryStatus')
def updateMandatoryStatus():
    try:
        body = request.get_json() or {}
        update_list = body.get('updateList')
        
        if not update_list or not isinstance(update_list, list):
            return {**ResponseMessage.message422, "data": "Expected 'updateList' array in body"}

        result = callMethod.fnUpdateMandatoryStatus(update_list)
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@artifactBluePrint.get('/getArtifactTypes')
def getArtifactTypes():
    try:
        result = callMethod.fnGetArtifactTypes()
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@artifactBluePrint.get('/getMandatoryArtifactTypes')
def getMandatoryArtifactTypes():
    try:
        result = callMethod.fnGetMandatoryArtifactTypes()
        return jsonify(result)
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


@artifactBluePrint.put('/updateArtifactState/<artifactId>')
def updateArtifactState(artifactId):
    try:
        body = request.get_json() or {}
        workflowId = body.get('workflowId')
        state = body.get('state', '').strip()
        assignedTo = body.get('assignedTo', [])
        userId = body.get('userId', '').strip()
        comments = body.get('comments', '').strip()

        result = callMethod.fnUpdateArtifactState(
            artifactId=artifactId,
            workflowId=workflowId,
            state=state,
            assignedTo=assignedTo,
            userId=userId,
            comments=comments
        )
        return jsonify(result)

    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
