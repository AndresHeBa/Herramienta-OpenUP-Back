from datetime import datetime
from bson import ObjectId
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage

dbConnLocal = HelperFunctions.dbConnection()

# HU-025: Gestión de usuarios y roles por proyecto

# Roles disponibles por proyecto
PROJECT_ROLES = [
    'author',      # Autor - crea artefactos
    'reviewer',    # Revisor - revisa y aprueba artefactos
    'po',          # Product Owner - gestiona backlog y prioridades
    'sm',          # Scrum Master - facilita proceso
    'developer',   # Desarrollador - implementa funcionalidades
    'tester',      # Tester - realiza pruebas
    'admin'        # Admin del proyecto - permisos completos
]

def fnInviteMember(project_id, user_id, roles, invited_by, notification_email=None):
    """
    Invita un usuario a un proyecto con roles específicos
    
    Args:
        project_id: ID del proyecto
        user_id: ID del usuario a invitar
        roles: Lista de roles a asignar ['author', 'reviewer', etc.]
        invited_by: ID del usuario que envía la invitación
        notification_email: Email opcional para notificación
    
    Returns:
        Response con la invitación creada
    """
    try:
        # Validaciones
        if not project_id or not user_id or not roles:
            return {**ResponseMessage.message422, "data": "Missing required fields"}
        
        if not isinstance(roles, list):
            return {**ResponseMessage.message422, "data": "Roles must be a list"}
        
        # Validar que los roles sean válidos
        invalid_roles = [r for r in roles if r not in PROJECT_ROLES]
        if invalid_roles:
            return {**ResponseMessage.message422, "data": f"Invalid roles: {invalid_roles}"}
        
        # Verificar que el proyecto existe
        try:
            proj_id = ObjectId(project_id) if ObjectId.is_valid(project_id) else None
        except:
            proj_id = None
            
        if proj_id:
            project = dbConnLocal.clProjects.find_one({'_id': proj_id})
        else:
            project = dbConnLocal.clProjects.find_one({'identifier': project_id})
        
        if not project:
            return {**ResponseMessage.message404, "data": "Project not found"}
        
        project_id = str(project['_id'])
        
        # Verificar que el usuario no está ya en el proyecto
        existing_member = dbConnLocal.clProjectMembers.find_one({
            'projectId': project_id,
            'userId': user_id,
            'status': {'$in': ['pending', 'active']}
        })
        
        if existing_member:
            return {**ResponseMessage.message422, "data": "User already invited or member"}
        
        # Crear invitación
        invitation = {
            'projectId': project_id,
            'userId': user_id,
            'roles': roles,
            'status': 'pending',  # pending, active, rejected, removed
            'invitedBy': invited_by,
            'invitedAt': datetime.now(),
            'notificationEmail': notification_email,
            'notificationSent': False,
            'acceptedAt': None,
            'rejectedAt': None
        }
        
        result = dbConnLocal.clProjectMembers.insert_one(invitation)
        invitation['_id'] = str(result.inserted_id)
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=invited_by,
            action_type='create',
            entity_type='project',
            entity_id=project_id,
            details={
                'action': 'invite_member',
                'invitedUser': user_id,
                'roles': roles
            },
            project_id=project_id
        )
        
        # TODO: Enviar notificación por email
        # _send_invitation_notification(invitation)
        
        return {
            **ResponseMessage.message200,
            "data": invitation,
            "message": "Member invited successfully"
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnAcceptInvitation(invitation_id, user_id):
    """
    Acepta una invitación a un proyecto
    
    Args:
        invitation_id: ID de la invitación
        user_id: ID del usuario que acepta
    
    Returns:
        Response con la invitación actualizada
    """
    try:
        if not ObjectId.is_valid(invitation_id):
            return {**ResponseMessage.message422, "data": "Invalid invitation ID"}
        
        invitation = dbConnLocal.clProjectMembers.find_one({
            '_id': ObjectId(invitation_id),
            'userId': user_id,
            'status': 'pending'
        })
        
        if not invitation:
            return {**ResponseMessage.message404, "data": "Invitation not found or already processed"}
        
        # Actualizar estado a activo
        result = dbConnLocal.clProjectMembers.update_one(
            {'_id': ObjectId(invitation_id)},
            {
                '$set': {
                    'status': 'active',
                    'acceptedAt': datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return {**ResponseMessage.message500, "data": "Failed to update invitation"}
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=user_id,
            action_type='edit',
            entity_type='project',
            entity_id=invitation['projectId'],
            details={
                'action': 'accept_invitation',
                'roles': invitation['roles']
            },
            project_id=invitation['projectId']
        )
        
        invitation['status'] = 'active'
        invitation['acceptedAt'] = datetime.now()
        invitation['_id'] = str(invitation['_id'])
        
        return {
            **ResponseMessage.message200,
            "data": invitation,
            "message": "Invitation accepted successfully"
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnRejectInvitation(invitation_id, user_id):
    """
    Rechaza una invitación a un proyecto
    """
    try:
        if not ObjectId.is_valid(invitation_id):
            return {**ResponseMessage.message422, "data": "Invalid invitation ID"}
        
        invitation = dbConnLocal.clProjectMembers.find_one({
            '_id': ObjectId(invitation_id),
            'userId': user_id,
            'status': 'pending'
        })
        
        if not invitation:
            return {**ResponseMessage.message404, "data": "Invitation not found or already processed"}
        
        result = dbConnLocal.clProjectMembers.update_one(
            {'_id': ObjectId(invitation_id)},
            {
                '$set': {
                    'status': 'rejected',
                    'rejectedAt': datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return {**ResponseMessage.message500, "data": "Failed to update invitation"}
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=user_id,
            action_type='edit',
            entity_type='project',
            entity_id=invitation['projectId'],
            details={
                'action': 'reject_invitation'
            },
            project_id=invitation['projectId']
        )
        
        return {
            **ResponseMessage.message200,
            "message": "Invitation rejected successfully"
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetProjectMembers(project_id, status=None):
    """
    Obtiene los miembros de un proyecto
    
    Args:
        project_id: ID del proyecto
        status: Filtrar por estado (pending, active, rejected, removed)
    
    Returns:
        Response con lista de miembros
    """
    try:
        # Normalizar project_id
        try:
            proj_id = ObjectId(project_id) if ObjectId.is_valid(project_id) else None
        except:
            proj_id = None
            
        if proj_id:
            project = dbConnLocal.clProjects.find_one({'_id': proj_id})
        else:
            project = dbConnLocal.clProjects.find_one({'identifier': project_id})
        
        if not project:
            return {**ResponseMessage.message404, "data": "Project not found"}
        
        project_id = str(project['_id'])
        
        # Construir query
        query = {'projectId': project_id}
        if status:
            if isinstance(status, list):
                query['status'] = {'$in': status}
            else:
                query['status'] = status
        
        # Obtener miembros
        members = list(dbConnLocal.clProjectMembers.find(query).sort('invitedAt', -1))
        
        # Convertir ObjectId a string y enriquecer con datos de usuario
        for member in members:
            member['_id'] = str(member['_id'])
            
            # Obtener información del usuario
            # Intentar primero como ObjectId, si falla buscar como string
            try:
                user = dbConnLocal.clUsers.find_one({'_id': ObjectId(member['userId'])})
            except:
                user = dbConnLocal.clUsers.find_one({'_id': member['userId']})
            
            if user:
                member['userInfo'] = {
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'active': user.get('active', True)
                }
            
            # Obtener información del invitador
            if member.get('invitedBy'):
                try:
                    inviter = dbConnLocal.clUsers.find_one({'_id': ObjectId(member['invitedBy'])})
                except:
                    inviter = dbConnLocal.clUsers.find_one({'_id': member['invitedBy']})
                    
                if inviter:
                    member['inviterInfo'] = {
                        'username': inviter.get('username')
                    }
        
        return {
            **ResponseMessage.message200,
            "data": {
                "members": members,
                "totalCount": len(members),
                "projectId": project_id,
                "projectName": project.get('name'),
                "projectIdentifier": project.get('identifier')
            }
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateMemberRoles(member_id, roles, updated_by):
    """
    Actualiza los roles de un miembro del proyecto
    
    Args:
        member_id: ID del registro de membresía
        roles: Nueva lista de roles
        updated_by: ID del usuario que actualiza
    
    Returns:
        Response con el miembro actualizado
    """
    try:
        if not ObjectId.is_valid(member_id):
            return {**ResponseMessage.message422, "data": "Invalid member ID"}
        
        if not isinstance(roles, list):
            return {**ResponseMessage.message422, "data": "Roles must be a list"}
        
        # Validar roles
        invalid_roles = [r for r in roles if r not in PROJECT_ROLES]
        if invalid_roles:
            return {**ResponseMessage.message422, "data": f"Invalid roles: {invalid_roles}"}
        
        member = dbConnLocal.clProjectMembers.find_one({'_id': ObjectId(member_id)})
        
        if not member:
            return {**ResponseMessage.message404, "data": "Member not found"}
        
        old_roles = member.get('roles', [])
        
        result = dbConnLocal.clProjectMembers.update_one(
            {'_id': ObjectId(member_id)},
            {
                '$set': {
                    'roles': roles,
                    'updatedAt': datetime.now(),
                    'updatedBy': updated_by
                }
            }
        )
        
        if result.modified_count == 0:
            return {**ResponseMessage.message500, "data": "Failed to update member roles"}
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=updated_by,
            action_type='edit',
            entity_type='project',
            entity_id=member['projectId'],
            details={
                'action': 'update_member_roles',
                'userId': member['userId'],
                'oldRoles': old_roles,
                'newRoles': roles
            },
            project_id=member['projectId']
        )
        
        member['roles'] = roles
        member['_id'] = str(member['_id'])
        
        return {
            **ResponseMessage.message200,
            "data": member,
            "message": "Member roles updated successfully"
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnRemoveMember(member_id, removed_by):
    """
    Remueve un miembro del proyecto (baja lógica)
    
    Args:
        member_id: ID del registro de membresía
        removed_by: ID del usuario que remueve
    
    Returns:
        Response confirmando la remoción
    """
    try:
        if not ObjectId.is_valid(member_id):
            return {**ResponseMessage.message422, "data": "Invalid member ID"}
        
        member = dbConnLocal.clProjectMembers.find_one({'_id': ObjectId(member_id)})
        
        if not member:
            return {**ResponseMessage.message404, "data": "Member not found"}
        
        result = dbConnLocal.clProjectMembers.update_one(
            {'_id': ObjectId(member_id)},
            {
                '$set': {
                    'status': 'removed',
                    'removedAt': datetime.now(),
                    'removedBy': removed_by
                }
            }
        )
        
        if result.modified_count == 0:
            return {**ResponseMessage.message500, "data": "Failed to remove member"}
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=removed_by,
            action_type='delete',
            entity_type='project',
            entity_id=member['projectId'],
            details={
                'action': 'remove_member',
                'userId': member['userId'],
                'roles': member.get('roles', [])
            },
            project_id=member['projectId']
        )
        
        return {
            **ResponseMessage.message200,
            "message": "Member removed successfully"
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetUserProjects(user_id, status='active'):
    """
    Obtiene los proyectos en los que un usuario es miembro
    
    Args:
        user_id: ID del usuario
        status: Filtrar por estado de membresía
    
    Returns:
        Response con lista de proyectos
    """
    try:
        query = {'userId': user_id}
        if status:
            query['status'] = status
        
        memberships = list(dbConnLocal.clProjectMembers.find(query))
        
        projects = []
        for membership in memberships:
            try:
                project = dbConnLocal.clProjects.find_one({'_id': ObjectId(membership['projectId'])})
            except:
                project = dbConnLocal.clProjects.find_one({'_id': membership['projectId']})
                
            if project:
                project['_id'] = str(project['_id'])
                project['memberRoles'] = membership.get('roles', [])
                project['memberStatus'] = membership.get('status')
                project['joinedAt'] = membership.get('acceptedAt')
                projects.append(project)
        
        return {
            **ResponseMessage.message200,
            "data": {
                "projects": projects,
                "totalCount": len(projects)
            }
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnCheckUserProjectAccess(user_id, project_id, required_role=None):
    """
    Verifica si un usuario tiene acceso a un proyecto
    
    Args:
        user_id: ID del usuario
        project_id: ID del proyecto
        required_role: Rol específico requerido (opcional)
    
    Returns:
        Dict con hasAccess (bool), roles (list), y status
    """
    try:
        # Normalizar project_id
        try:
            proj_id = ObjectId(project_id) if ObjectId.is_valid(project_id) else None
        except:
            proj_id = None
            
        if proj_id:
            project = dbConnLocal.clProjects.find_one({'_id': proj_id})
        else:
            project = dbConnLocal.clProjects.find_one({'identifier': project_id})
        
        if not project:
            return {
                'hasAccess': False,
                'roles': [],
                'status': None,
                'error': 'Project not found'
            }
        
        project_id = str(project['_id'])
        
        member = dbConnLocal.clProjectMembers.find_one({
            'projectId': project_id,
            'userId': user_id,
            'status': 'active'
        })
        
        if not member:
            return {
                'hasAccess': False,
                'roles': [],
                'status': None
            }
        
        roles = member.get('roles', [])
        has_access = True
        
        if required_role:
            has_access = required_role in roles or 'admin' in roles
        
        return {
            'hasAccess': has_access,
            'roles': roles,
            'status': member.get('status'),
            'memberId': str(member['_id'])
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return {
            'hasAccess': False,
            'roles': [],
            'status': None,
            'error': 'Error checking access'
        }


def fnGetPendingInvitations(user_id):
    """
    Obtiene las invitaciones pendientes de un usuario
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Response con lista de invitaciones pendientes
    """
    try:
        invitations = list(dbConnLocal.clProjectMembers.find({
            'userId': user_id,
            'status': 'pending'
        }).sort('invitedAt', -1))
        
        # Enriquecer con datos del proyecto
        for invitation in invitations:
            invitation['_id'] = str(invitation['_id'])
            
            try:
                project = dbConnLocal.clProjects.find_one({'_id': ObjectId(invitation['projectId'])})
            except:
                project = dbConnLocal.clProjects.find_one({'_id': invitation['projectId']})
                
            if project:
                invitation['projectInfo'] = {
                    'name': project.get('name'),
                    'identifier': project.get('identifier'),
                    'description': project.get('description')
                }
            
            # Información del invitador
            if invitation.get('invitedBy'):
                try:
                    inviter = dbConnLocal.clUsers.find_one({'_id': ObjectId(invitation['invitedBy'])})
                except:
                    inviter = dbConnLocal.clUsers.find_one({'_id': invitation['invitedBy']})
                    
                if inviter:
                    invitation['inviterInfo'] = {
                        'username': inviter.get('username'),
                        'email': inviter.get('email')
                    }
        
        return {
            **ResponseMessage.message200,
            "data": {
                "invitations": invitations,
                "totalCount": len(invitations)
            }
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
