from flask import Blueprint, jsonify, request
from datetime import datetime

auditBluePrint = Blueprint('auditBluePrint', __name__, url_prefix='/api/audit')

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from BackEnd.GlobalInfo.permissions import requireAction

# Functions import
import BackEnd.Functions.auditFunctions as callMethod


@auditBluePrint.route('/logs', methods=['GET'])
@requireAction('view_audit')
def getAuditLogs():
    """
    Obtiene logs de auditoría con filtros opcionales
    
    GET /api/audit/logs?projectId=xxx&userId=xxx&actionType=create&limit=50&skip=0
    
    Query params:
        - projectId: Filtrar por proyecto
        - userId: Filtrar por usuario
        - actionType: Filtrar por tipo de acción (puede ser múltiple separado por comas)
        - entityType: Filtrar por tipo de entidad (puede ser múltiple separado por comas)
        - entityId: Filtrar por ID de entidad específica
        - startDate: Fecha de inicio (ISO format)
        - endDate: Fecha de fin (ISO format)
        - limit: Número de registros (default: 100)
        - skip: Offset para paginación (default: 0)
        - sortField: Campo de ordenamiento (default: timestamp)
        - sortOrder: Orden (1 asc, -1 desc, default: -1)
    """
    try:
        filters = {}
        
        # Filtros opcionales
        if request.args.get('projectId'):
            filters['projectId'] = request.args.get('projectId')
        
        if request.args.get('userId'):
            filters['userId'] = request.args.get('userId')
        
        if request.args.get('actionType'):
            action_types = request.args.get('actionType').split(',')
            filters['actionType'] = action_types if len(action_types) > 1 else action_types[0]
        
        if request.args.get('entityType'):
            entity_types = request.args.get('entityType').split(',')
            filters['entityType'] = entity_types if len(entity_types) > 1 else entity_types[0]
        
        if request.args.get('entityId'):
            filters['entityId'] = request.args.get('entityId')
        
        # Filtro por fechas
        if request.args.get('startDate'):
            try:
                filters['startDate'] = datetime.fromisoformat(request.args.get('startDate'))
            except:
                pass
        
        if request.args.get('endDate'):
            try:
                filters['endDate'] = datetime.fromisoformat(request.args.get('endDate'))
            except:
                pass
        
        # Paginación
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        sort_field = request.args.get('sortField', 'timestamp')
        sort_order = int(request.args.get('sortOrder', -1))
        
        result = callMethod.fnGetAuditLogs(
            filters=filters if filters else None,
            limit=limit,
            skip=skip,
            sort_field=sort_field,
            sort_order=sort_order
        )
        
        return jsonify(result)
    
    except Exception as e:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@auditBluePrint.route('/project/<projectId>', methods=['GET'])
@requireAction('view_audit')
def getProjectAuditHistory(projectId):
    """
    Obtiene el historial completo de auditoría de un proyecto
    
    GET /api/audit/project/<projectId>?limit=100&skip=0
    """
    try:
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        result = callMethod.fnGetProjectAuditHistory(projectId, limit, skip)
        
        return jsonify(result)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@auditBluePrint.route('/entity/<entityType>/<entityId>', methods=['GET'])
@requireAction('view_audit')
def getEntityAuditHistory(entityType, entityId):
    """
    Obtiene el historial de auditoría de una entidad específica
    
    GET /api/audit/entity/<entityType>/<entityId>?limit=50&skip=0
    """
    try:
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        result = callMethod.fnGetEntityAuditHistory(entityType, entityId, limit, skip)
        
        return jsonify(result)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@auditBluePrint.route('/user/<userId>', methods=['GET'])
@requireAction('view_audit')
def getUserAuditHistory(userId):
    """
    Obtiene el historial de acciones de un usuario específico
    
    GET /api/audit/user/<userId>?limit=100&skip=0&startDate=xxx&endDate=xxx
    """
    try:
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        start_date = None
        end_date = None
        
        if request.args.get('startDate'):
            try:
                start_date = datetime.fromisoformat(request.args.get('startDate'))
            except:
                pass
        
        if request.args.get('endDate'):
            try:
                end_date = datetime.fromisoformat(request.args.get('endDate'))
            except:
                pass
        
        result = callMethod.fnGetUserAuditHistory(userId, limit, skip, start_date, end_date)
        
        return jsonify(result)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@auditBluePrint.route('/export', methods=['GET'])
@requireAction('export_audit')
def exportAuditLogs():
    """
    Exporta logs de auditoría en formato JSON o CSV
    
    GET /api/audit/export?format=json&projectId=xxx&startDate=xxx&endDate=xxx
    
    Query params:
        - format: 'json' o 'csv' (default: json)
        - Mismos filtros que /logs
    """
    try:
        export_format = request.args.get('format', 'json').lower()
        
        filters = {}
        if request.args.get('projectId'):
            filters['projectId'] = request.args.get('projectId')
        
        if request.args.get('userId'):
            filters['userId'] = request.args.get('userId')
        
        if request.args.get('actionType'):
            action_types = request.args.get('actionType').split(',')
            filters['actionType'] = action_types if len(action_types) > 1 else action_types[0]
        
        if request.args.get('entityType'):
            entity_types = request.args.get('entityType').split(',')
            filters['entityType'] = entity_types if len(entity_types) > 1 else entity_types[0]
        
        if request.args.get('startDate'):
            try:
                filters['startDate'] = datetime.fromisoformat(request.args.get('startDate'))
            except:
                pass
        
        if request.args.get('endDate'):
            try:
                filters['endDate'] = datetime.fromisoformat(request.args.get('endDate'))
            except:
                pass
        
        result = callMethod.fnExportAuditLogs(
            filters=filters if filters else None,
            export_format=export_format
        )
        
        if result.get('intCode') == 200 and export_format == 'csv':
            from flask import Response
            csv_data = result['Result']['data']
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                }
            )
        
        return jsonify(result)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@auditBluePrint.route('/stats', methods=['GET'])
@requireAction('view_audit')
def getAuditStats():
    """
    Obtiene estadísticas de auditoría
    
    GET /api/audit/stats?projectId=xxx&startDate=xxx&endDate=xxx
    """
    try:
        project_id = request.args.get('projectId')
        
        start_date = None
        end_date = None
        
        if request.args.get('startDate'):
            try:
                start_date = datetime.fromisoformat(request.args.get('startDate'))
            except:
                pass
        
        if request.args.get('endDate'):
            try:
                end_date = datetime.fromisoformat(request.args.get('endDate'))
            except:
                pass
        
        result = callMethod.fnGetAuditStats(project_id, start_date, end_date)
        
        return jsonify(result)
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500


@auditBluePrint.route('/log', methods=['POST'])
@requireAction('create')
def createAuditLog():
    """
    Crea manualmente un registro de auditoría (para casos especiales)
    
    POST /api/audit/log
    Body: {
        "userId": "xxx",
        "actionType": "create",
        "entityType": "artifact",
        "entityId": "xxx",
        "projectId": "xxx",
        "details": {}
    }
    """
    try:
        body = request.json or {}
        
        user_id = body.get('userId')
        action_type = body.get('actionType')
        entity_type = body.get('entityType')
        entity_id = body.get('entityId')
        project_id = body.get('projectId')
        details = body.get('details', {})
        
        if not all([user_id, action_type, entity_type]):
            return jsonify({
                **ResponseMessage.message422,
                'data': 'userId, actionType, and entityType are required'
            }), 422
        
        log_id = callMethod.fnLogAuditAction(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            project_id=project_id
        )
        
        if log_id:
            return jsonify({
                **ResponseMessage.message200,
                'Result': {'logId': str(log_id)}
            })
        else:
            return jsonify(ResponseMessage.message500), 500
    
    except Exception:
        HelperFunctions.PrintException()
        return jsonify(ResponseMessage.message500), 500
