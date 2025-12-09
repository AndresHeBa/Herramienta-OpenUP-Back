from datetime import datetime
from bson import ObjectId
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage

dbConnLocal = HelperFunctions.dbConnection()

# HU-024: Auditoría y registro de cambios (trail)

def fnLogAuditAction(user_id, action_type, entity_type, entity_id, details=None, project_id=None):
    """
    Registra una acción de auditoría en el sistema
    
    Args:
        user_id: ID del usuario que realiza la acción
        action_type: Tipo de acción ('create', 'edit', 'delete', 'status_change', 'version_create', 'move', 'archive', 'restore', 'export', 'import')
        entity_type: Tipo de entidad afectada ('project', 'artifact', 'iteration', 'microincrement', 'build', 'workflow', 'configuration', 'plan')
        entity_id: ID de la entidad afectada
        details: Detalles adicionales (dict con información específica del cambio)
        project_id: ID del proyecto relacionado (opcional pero recomendado)
    
    Returns:
        ObjectId del registro de auditoría creado
    """
    try:
        audit_entry = {
            'userId': user_id,
            'actionType': action_type,
            'entityType': entity_type,
            'entityId': str(entity_id) if entity_id else None,
            'projectId': str(project_id) if project_id else None,
            'timestamp': datetime.now(),
            'details': details or {},
            'ipAddress': None,  # Se puede agregar desde el request en Directions
            'userAgent': None   # Se puede agregar desde el request en Directions
        }
        
        result = dbConnLocal.clAuditLog.insert_one(audit_entry)
        return result.inserted_id
        
    except Exception:
        HelperFunctions.PrintException()
        return None


def fnGetAuditLogs(filters=None, limit=100, skip=0, sort_field='timestamp', sort_order=-1):
    """
    Obtiene logs de auditoría con filtros opcionales
    
    Args:
        filters: Dict con filtros (projectId, userId, actionType, entityType, startDate, endDate)
        limit: Número máximo de registros a retornar
        skip: Número de registros a saltar (para paginación)
        sort_field: Campo por el cual ordenar
        sort_order: Orden (1 ascendente, -1 descendente)
    
    Returns:
        Response con lista de logs y total count
    """
    try:
        query = {}
        
        if filters:
            if 'projectId' in filters and filters['projectId']:
                query['projectId'] = filters['projectId']
            
            if 'userId' in filters and filters['userId']:
                query['userId'] = filters['userId']
            
            if 'actionType' in filters and filters['actionType']:
                if isinstance(filters['actionType'], list):
                    query['actionType'] = {'$in': filters['actionType']}
                else:
                    query['actionType'] = filters['actionType']
            
            if 'entityType' in filters and filters['entityType']:
                if isinstance(filters['entityType'], list):
                    query['entityType'] = {'$in': filters['entityType']}
                else:
                    query['entityType'] = filters['entityType']
            
            if 'entityId' in filters and filters['entityId']:
                query['entityId'] = filters['entityId']
            
            # Filtro por rango de fechas
            if 'startDate' in filters or 'endDate' in filters:
                date_query = {}
                if 'startDate' in filters:
                    date_query['$gte'] = filters['startDate']
                if 'endDate' in filters:
                    date_query['$lte'] = filters['endDate']
                if date_query:
                    query['timestamp'] = date_query
        
        # Obtener total count
        total_count = dbConnLocal.clAuditLog.count_documents(query)
        
        # Obtener logs
        logs = list(dbConnLocal.clAuditLog.find(query)
                   .sort(sort_field, sort_order)
                   .skip(skip)
                   .limit(limit))
        
        # Convertir ObjectIds a strings
        for log in logs:
            log['_id'] = str(log['_id'])
            if isinstance(log.get('timestamp'), datetime):
                log['timestamp'] = log['timestamp'].isoformat()
        
        return {
            **ResponseMessage.message200,
            'Result': {
                'logs': logs,
                'totalCount': total_count,
                'page': skip // limit + 1 if limit > 0 else 1,
                'pageSize': limit,
                'totalPages': (total_count + limit - 1) // limit if limit > 0 else 1
            }
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetProjectAuditHistory(project_id, limit=100, skip=0):
    """
    Obtiene el historial completo de auditoría de un proyecto
    
    Args:
        project_id: ID del proyecto
        limit: Número máximo de registros
        skip: Offset para paginación
    
    Returns:
        Response con historial de auditoría del proyecto
    """
    try:
        if not project_id:
            return {
                **ResponseMessage.message202,
                'data': 'project_id is required'
            }
        
        return fnGetAuditLogs(
            filters={'projectId': str(project_id)},
            limit=limit,
            skip=skip
        )
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetEntityAuditHistory(entity_type, entity_id, limit=50, skip=0):
    """
    Obtiene el historial de auditoría de una entidad específica
    
    Args:
        entity_type: Tipo de entidad ('artifact', 'iteration', etc.)
        entity_id: ID de la entidad
        limit: Número máximo de registros
        skip: Offset para paginación
    
    Returns:
        Response con historial de la entidad
    """
    try:
        if not entity_type or not entity_id:
            return {
                **ResponseMessage.message202,
                'data': 'entity_type and entity_id are required'
            }
        
        return fnGetAuditLogs(
            filters={
                'entityType': entity_type,
                'entityId': str(entity_id)
            },
            limit=limit,
            skip=skip
        )
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetUserAuditHistory(user_id, limit=100, skip=0, start_date=None, end_date=None):
    """
    Obtiene el historial de acciones de un usuario específico
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de registros
        skip: Offset para paginación
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
    
    Returns:
        Response con historial del usuario
    """
    try:
        if not user_id:
            return {
                **ResponseMessage.message202,
                'data': 'user_id is required'
            }
        
        filters = {'userId': user_id}
        
        if start_date:
            filters['startDate'] = start_date
        if end_date:
            filters['endDate'] = end_date
        
        return fnGetAuditLogs(
            filters=filters,
            limit=limit,
            skip=skip
        )
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnExportAuditLogs(filters=None, export_format='json'):
    """
    Exporta logs de auditoría en formato JSON o CSV
    
    Args:
        filters: Filtros para los logs a exportar
        export_format: Formato de exportación ('json' o 'csv')
    
    Returns:
        Response con datos exportados
    """
    try:
        # Obtener todos los logs sin límite
        result = fnGetAuditLogs(filters=filters, limit=0, skip=0)
        
        if result.get('intCode') != 200:
            return result
        
        logs = result['Result']['logs']
        
        if export_format == 'json':
            return {
                **ResponseMessage.message200,
                'Result': {
                    'format': 'json',
                    'data': logs,
                    'exportDate': datetime.now().isoformat(),
                    'totalRecords': len(logs)
                }
            }
        
        elif export_format == 'csv':
            # Generar CSV
            import csv
            import io
            
            output = io.StringIO()
            if logs:
                fieldnames = ['_id', 'userId', 'actionType', 'entityType', 'entityId', 'projectId', 'timestamp', 'details']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for log in logs:
                    # Convertir details dict a string para CSV
                    row = {k: v for k, v in log.items() if k in fieldnames}
                    if 'details' in row:
                        row['details'] = str(row['details'])
                    writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                **ResponseMessage.message200,
                'Result': {
                    'format': 'csv',
                    'data': csv_content,
                    'exportDate': datetime.now().isoformat(),
                    'totalRecords': len(logs)
                }
            }
        
        else:
            return {
                **ResponseMessage.message202,
                'data': 'unsupported export format'
            }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetAuditStats(project_id=None, start_date=None, end_date=None):
    """
    Obtiene estadísticas de auditoría
    
    Args:
        project_id: ID del proyecto (opcional)
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
    
    Returns:
        Response con estadísticas de auditoría
    """
    try:
        match_query = {}
        
        if project_id:
            match_query['projectId'] = str(project_id)
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                match_query['timestamp'] = date_query
        
        # Agregación por tipo de acción
        action_stats = list(dbConnLocal.clAuditLog.aggregate([
            {'$match': match_query},
            {'$group': {
                '_id': '$actionType',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]))
        
        # Agregación por tipo de entidad
        entity_stats = list(dbConnLocal.clAuditLog.aggregate([
            {'$match': match_query},
            {'$group': {
                '_id': '$entityType',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]))
        
        # Top usuarios más activos
        user_stats = list(dbConnLocal.clAuditLog.aggregate([
            {'$match': match_query},
            {'$group': {
                '_id': '$userId',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]))
        
        # Total de acciones
        total_actions = dbConnLocal.clAuditLog.count_documents(match_query)
        
        return {
            **ResponseMessage.message200,
            'Result': {
                'totalActions': total_actions,
                'actionTypeStats': action_stats,
                'entityTypeStats': entity_stats,
                'topUsers': user_stats
            }
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
