from flask import Blueprint, jsonify, request
from datetime import datetime

projectMembersBluePrint = Blueprint('projectMembersBluePrint', __name__, url_prefix='/api/project-members')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.GlobalInfo.permissions import requireAction

# Functions import
import BackEnd.Functions.projectMembersFunctions as callMethod


@projectMembersBluePrint.route('/invite', methods=['POST'])
# @requireAction('manage_team')  # Temporalmente deshabilitado para debugging
def inviteMember():
    """
    Invita un usuario a un proyecto
    
    POST /api/project-members/invite
    Body:
    {
        "projectId": "project-id or identifier",
        "userId": "user-id",
        "roles": ["author", "reviewer"],
        "invitedBy": "inviter-user-id",
        "notificationEmail": "optional@email.com"
    }
    """
    try:
        data = request.get_json()
        
        print(f"DEBUG - Invite member request data: {data}")
        
        if not data:
            return jsonify({**ResponseMessage.message422, "data": "Missing request body"}), 422
        
        project_id = data.get('projectId')
        user_id = data.get('userId')
        roles = data.get('roles')
        invited_by = data.get('invitedBy')
        notification_email = data.get('notificationEmail')
        
        print(f"DEBUG - Calling fnInviteMember with: project_id={project_id}, user_id={user_id}, roles={roles}")
        
        result = callMethod.fnInviteMember(
            project_id=project_id,
            user_id=user_id,
            roles=roles,
            invited_by=invited_by,
            notification_email=notification_email
        )
        
        print(f"DEBUG - fnInviteMember result: {result}")
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception as e:
        HelperFunctions.PrintException()
        print(f"ERROR - Exception in inviteMember: {str(e)}")
        return jsonify({**ResponseMessage.message500, "error": str(e)}), 500


@projectMembersBluePrint.route('/accept/<invitation_id>', methods=['PUT'])
def acceptInvitation(invitation_id):
    """
    Acepta una invitación a un proyecto
    
    PUT /api/project-members/accept/<invitation_id>
    Body:
    {
        "userId": "user-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({**ResponseMessage.message422, "data": "Missing request body"}), 422
        
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({**ResponseMessage.message422, "data": "userId required"}), 422
        
        result = callMethod.fnAcceptInvitation(
            invitation_id=invitation_id,
            user_id=user_id
        )
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/reject/<invitation_id>', methods=['PUT'])
def rejectInvitation(invitation_id):
    """
    Rechaza una invitación a un proyecto
    
    PUT /api/project-members/reject/<invitation_id>
    Body:
    {
        "userId": "user-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({**ResponseMessage.message422, "data": "Missing request body"}), 422
        
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({**ResponseMessage.message422, "data": "userId required"}), 422
        
        result = callMethod.fnRejectInvitation(
            invitation_id=invitation_id,
            user_id=user_id
        )
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/project/<project_id>', methods=['GET'])
@requireAction('view_team')
def getProjectMembers(project_id):
    """
    Obtiene los miembros de un proyecto
    
    GET /api/project-members/project/<project_id>?status=active,pending
    
    Query params:
        - status: Filtrar por estado (puede ser múltiple separado por comas)
    """
    try:
        status_param = request.args.get('status')
        status = None
        
        if status_param:
            status_list = status_param.split(',')
            status = status_list if len(status_list) > 1 else status_list[0]
        
        result = callMethod.fnGetProjectMembers(
            project_id=project_id,
            status=status
        )
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/update-roles/<member_id>', methods=['PUT'])
@requireAction('manage_team')
def updateMemberRoles(member_id):
    """
    Actualiza los roles de un miembro
    
    PUT /api/project-members/update-roles/<member_id>
    Body:
    {
        "roles": ["author", "developer"],
        "updatedBy": "user-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({**ResponseMessage.message422, "data": "Missing request body"}), 422
        
        roles = data.get('roles')
        updated_by = data.get('updatedBy')
        
        if not roles or not updated_by:
            return jsonify({**ResponseMessage.message422, "data": "roles and updatedBy required"}), 422
        
        result = callMethod.fnUpdateMemberRoles(
            member_id=member_id,
            roles=roles,
            updated_by=updated_by
        )
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/remove/<member_id>', methods=['DELETE'])
@requireAction('manage_team')
def removeMember(member_id):
    """
    Remueve un miembro del proyecto
    
    DELETE /api/project-members/remove/<member_id>
    Body:
    {
        "removedBy": "user-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({**ResponseMessage.message422, "data": "Missing request body"}), 422
        
        removed_by = data.get('removedBy')
        
        if not removed_by:
            return jsonify({**ResponseMessage.message422, "data": "removedBy required"}), 422
        
        result = callMethod.fnRemoveMember(
            member_id=member_id,
            removed_by=removed_by
        )
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/user/<user_id>/projects', methods=['GET'])
def getUserProjects(user_id):
    """
    Obtiene los proyectos de un usuario
    
    GET /api/project-members/user/<user_id>/projects?status=active
    
    Query params:
        - status: Filtrar por estado de membresía (default: active)
    """
    try:
        status = request.args.get('status', 'active')
        
        result = callMethod.fnGetUserProjects(
            user_id=user_id,
            status=status
        )
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/check-access', methods=['POST'])
def checkUserProjectAccess():
    """
    Verifica si un usuario tiene acceso a un proyecto
    
    POST /api/project-members/check-access
    Body:
    {
        "userId": "user-id",
        "projectId": "project-id",
        "requiredRole": "author" (opcional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({**ResponseMessage.message422, "data": "Missing request body"}), 422
        
        user_id = data.get('userId')
        project_id = data.get('projectId')
        required_role = data.get('requiredRole')
        
        if not user_id or not project_id:
            return jsonify({**ResponseMessage.message422, "data": "userId and projectId required"}), 422
        
        access_info = callMethod.fnCheckUserProjectAccess(
            user_id=user_id,
            project_id=project_id,
            required_role=required_role
        )
        
        return jsonify({
            **ResponseMessage.message200,
            "data": access_info
        }), 200
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/user/<user_id>/invitations', methods=['GET'])
def getPendingInvitations(user_id):
    """
    Obtiene las invitaciones pendientes de un usuario
    
    GET /api/project-members/user/<user_id>/invitations
    """
    try:
        result = callMethod.fnGetPendingInvitations(user_id=user_id)
        
        status_code = result.get('intCode', 500)
        return jsonify(result), status_code
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@projectMembersBluePrint.route('/roles', methods=['GET'])
def getAvailableRoles():
    """
    Obtiene la lista de roles disponibles para proyectos
    
    GET /api/project-members/roles
    """
    try:
        from BackEnd.Functions.projectMembersFunctions import PROJECT_ROLES
        
        roles_info = [
            {'id': 'author', 'name': 'Autor', 'description': 'Crea artefactos'},
            {'id': 'reviewer', 'name': 'Revisor', 'description': 'Revisa y aprueba artefactos'},
            {'id': 'po', 'name': 'Product Owner', 'description': 'Gestiona backlog y prioridades'},
            {'id': 'sm', 'name': 'Scrum Master', 'description': 'Facilita el proceso'},
            {'id': 'developer', 'name': 'Desarrollador', 'description': 'Implementa funcionalidades'},
            {'id': 'tester', 'name': 'Tester', 'description': 'Realiza pruebas'},
            {'id': 'admin', 'name': 'Admin', 'description': 'Permisos completos en el proyecto'}
        ]
        
        return jsonify({
            **ResponseMessage.message200,
            "data": {
                "roles": roles_info,
                "totalCount": len(roles_info)
            }
        }), 200
        
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500
