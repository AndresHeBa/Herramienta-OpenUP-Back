from flask import Blueprint, request, jsonify, send_file
from bson import ObjectId
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.Functions.projectClosureFunctions import (
    fnValidateProjectClosure,
    fnCloseProject,
    fnGetClosureDocument,
    fnReopenProject,
    fnGenerateClosurePDF
)
from BackEnd.GlobalInfo.permissions import requireAdmin, requireAction

# HU-026: Project Closure Blueprint
projectClosureBluePrint = Blueprint('projectClosure', __name__)

@projectClosureBluePrint.route('/api/project-closure/validate/<project_id>', methods=['GET'])
# @requireAction('view_project')  # Temporalmente comentado para testing
def validateClosure(project_id):
    """
    GET /api/project-closure/validate/<project_id>
    Valida si un proyecto puede cerrarse
    
    Response:
    {
        "intCode": 200,
        "data": {
            "canClose": bool,
            "missingArtifacts": [...],
            "warnings": [...],
            "projectId": "...",
            "projectName": "...",
            "projectIdentifier": "...",
            "currentStatus": "..."
        }
    }
    """
    try:
        print(f"DEBUG - Validate closure for project: {project_id}")
        
        # Obtener userId del header o session
        user_id = request.headers.get('X-User-Id', '1')  # Default para testing
        
        result = fnValidateProjectClosure(project_id, user_id)
        
        print(f"DEBUG - Validation result: {result}")
        
        return jsonify(result), result.get('intCode', 200)
        
    except Exception as e:
        print(f"ERROR - Exception in validateClosure: {str(e)}")
        HelperFunctions.PrintException()
        return jsonify({**ResponseMessage.message500, "error": str(e)}), 500


@projectClosureBluePrint.route('/api/project-closure/close', methods=['POST'])
# @requireAction('close_project')  # Temporalmente comentado para testing
def closeProject():
    """
    POST /api/project-closure/close
    Cierra un proyecto generando documento de cierre
    
    Body:
    {
        "projectId": "...",
        "forceClose": bool (optional),
        "justification": "..." (required if forceClose=true),
        "closureNotes": "..." (optional)
    }
    
    Response:
    {
        "intCode": 200,
        "data": {
            "projectId": "...",
            "closureDocument": {...},
            "closedAt": "...",
            "closureType": "normal|forced"
        }
    }
    """
    try:
        data = request.get_json()
        
        print(f"DEBUG - Close project request: {data}")
        
        project_id = data.get('projectId')
        force_close = data.get('forceClose', False)
        justification = data.get('justification')
        closure_notes = data.get('closureNotes')
        
        if not project_id:
            return jsonify({**ResponseMessage.message422, "data": "projectId required"}), 422
        
        # Obtener userId del header o session
        user_id = request.headers.get('X-User-Id', '1')  # Default para testing
        
        result = fnCloseProject(
            project_id=project_id,
            user_id=user_id,
            force_close=force_close,
            justification=justification,
            closure_notes=closure_notes
        )
        
        print(f"DEBUG - Close result: {result.get('intCode')}")
        
        return jsonify(result), result.get('intCode', 200)
        
    except Exception as e:
        print(f"ERROR - Exception in closeProject: {str(e)}")
        HelperFunctions.PrintException()
        return jsonify({**ResponseMessage.message500, "error": str(e)}), 500


@projectClosureBluePrint.route('/api/project-closure/document/<project_id>', methods=['GET'])
# @requireAction('view_project')  # Temporalmente comentado para testing
def getClosureDocument(project_id):
    """
    GET /api/project-closure/document/<project_id>
    Obtiene el documento de cierre de un proyecto
    
    Response:
    {
        "intCode": 200,
        "data": {
            "closureDocument": {...},
            "artifact": {...}
        }
    }
    """
    try:
        print(f"DEBUG - Get closure document for project: {project_id}")
        
        result = fnGetClosureDocument(project_id)
        
        return jsonify(result), result.get('intCode', 200)
        
    except Exception as e:
        print(f"ERROR - Exception in getClosureDocument: {str(e)}")
        HelperFunctions.PrintException()
        return jsonify({**ResponseMessage.message500, "error": str(e)}), 500


@projectClosureBluePrint.route('/api/project-closure/reopen', methods=['POST'])
@requireAdmin
def reopenProject():
    """
    POST /api/project-closure/reopen
    Reabre un proyecto cerrado (solo admin)
    
    Body:
    {
        "projectId": "...",
        "reason": "..."
    }
    
    Response:
    {
        "intCode": 200,
        "message": "Project reopened successfully"
    }
    """
    try:
        data = request.get_json()
        
        print(f"DEBUG - Reopen project request: {data}")
        
        project_id = data.get('projectId')
        reason = data.get('reason')
        
        if not project_id or not reason:
            return jsonify({**ResponseMessage.message422, "data": "projectId and reason required"}), 422
        
        # Obtener userId del header o session
        user_id = request.headers.get('X-User-Id', '1')  # Default para testing
        
        result = fnReopenProject(
            project_id=project_id,
            user_id=user_id,
            reason=reason
        )
        
        print(f"DEBUG - Reopen result: {result.get('intCode')}")
        
        return jsonify(result), result.get('intCode', 200)
        
    except Exception as e:
        print(f"ERROR - Exception in reopenProject: {str(e)}")
        HelperFunctions.PrintException()
        return jsonify({**ResponseMessage.message500, "error": str(e)}), 500


@projectClosureBluePrint.route('/api/project-closure/download-pdf/<project_id>', methods=['GET'])
# @requireAction('view_project')  # Temporalmente comentado para testing
def downloadClosurePDF(project_id):
    """
    GET /api/project-closure/download-pdf/<project_id>
    Descarga el documento de cierre como PDF
    
    Response:
    PDF file download
    """
    try:
        print(f"DEBUG - Generate closure PDF for project: {project_id}")
        
        # Buscar proyecto para obtener identificador
        from BackEnd.GlobalInfo.Helpers import dbConnection
        db = dbConnection()
        
        try:
            proj_id = ObjectId(project_id) if ObjectId.is_valid(project_id) else None
        except:
            proj_id = None
            
        if proj_id:
            project = db.clProjects.find_one({'_id': proj_id})
        else:
            project = db.clProjects.find_one({'identifier': project_id})
        
        if not project:
            return jsonify({**ResponseMessage.message404, "data": "Project not found"}), 404
        
        project_identifier = project.get('identifier', 'PROJECT')
        
        # Generar PDF
        pdf_buffer = fnGenerateClosurePDF(project_id)
        
        if not pdf_buffer:
            return jsonify({**ResponseMessage.message500, "data": "Failed to generate PDF"}), 500
        
        # Nombre del archivo
        filename = f"Cierre_{project_identifier}.pdf"
        
        print(f"DEBUG - PDF generated successfully: {filename}")
        
        # Enviar archivo
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"ERROR - Exception in downloadClosurePDF: {str(e)}")
        HelperFunctions.PrintException()
        return jsonify({**ResponseMessage.message500, "error": str(e)}), 500

