from datetime import datetime
from bson import ObjectId
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
from BackEnd.Functions.artifactFunctions import REQUIRED_ARTIFACTS
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

dbConnLocal = HelperFunctions.dbConnection()

# HU-026: Cierre de proyecto y checklist de entrega final

def fnValidateProjectClosure(project_id, user_id):
    """
    Valida si un proyecto puede cerrarse verificando artefactos obligatorios
    
    Args:
        project_id: ID del proyecto
        user_id: ID del usuario que solicita validación
    
    Returns:
        Response con validación: canClose (bool), missingArtifacts (list), warnings (list)
    """
    try:
        # Buscar proyecto
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
        
        project_identifier = project.get('identifier')
        phases = project.get('phases', [])
        
        missing_artifacts = []
        warnings = []
        
        # Verificar artefactos obligatorios por cada fase
        for phase in phases:
            phase_name = phase.get('name', '').lower()
            phase_normalized = phase_name.replace('ó', 'o').replace('í', 'i')
            
            # Mapeo de nombres de fases
            phase_map = {
                'incepcion': 'inception',
                'inception': 'inception',
                'elaboracion': 'elaboration',
                'elaboration': 'elaboration',
                'construccion': 'construction',
                'construction': 'construction',
                'transicion': 'transition',
                'transition': 'transition'
            }
            
            phase_key = phase_map.get(phase_normalized)
            if not phase_key or phase_key not in REQUIRED_ARTIFACTS:
                continue
            
            required = REQUIRED_ARTIFACTS[phase_key]
            
            for artifact_req in required:
                if not artifact_req.get('mandatory'):
                    continue
                
                artifact_type = artifact_req['type']
                
                # Buscar artefacto en BD
                artifact = dbConnLocal.clArtifacts.find_one({
                    'projectId': project_identifier,
                    'phase': phase_name,
                    'artifactType': artifact_type
                })
                
                if not artifact:
                    missing_artifacts.append({
                        'phase': phase_name,
                        'artifactType': artifact_type,
                        'reason': 'not_found'
                    })
                elif artifact.get('status') != 'Entregado':
                    warnings.append({
                        'phase': phase_name,
                        'artifactType': artifact_type,
                        'currentStatus': artifact.get('status', 'Unknown'),
                        'version': artifact.get('version', 1),
                        'reason': 'not_delivered'
                    })
        
        # Verificar estado del proyecto
        if project.get('status') == 'closed':
            return {
                **ResponseMessage.message422,
                "data": "Project is already closed"
            }
        
        can_close = len(missing_artifacts) == 0
        
        return {
            **ResponseMessage.message200,
            "data": {
                "canClose": can_close,
                "missingArtifacts": missing_artifacts,
                "warnings": warnings,
                "projectId": str(project['_id']),
                "projectName": project.get('name'),
                "projectIdentifier": project_identifier,
                "currentStatus": project.get('status')
            }
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnCloseProject(project_id, user_id, force_close=False, justification=None, closure_notes=None):
    """
    Cierra un proyecto generando documento de cierre y archivando
    
    Args:
        project_id: ID del proyecto
        user_id: ID del usuario que cierra (debe ser admin, po, o sm)
        force_close: Forzar cierre aunque falten artefactos (solo admin)
        justification: Justificación obligatoria si force_close=True
        closure_notes: Notas adicionales del cierre
    
    Returns:
        Response con documento de cierre generado
    """
    try:
        # Validar primero
        validation = fnValidateProjectClosure(project_id, user_id)
        if validation.get('intCode') != 200:
            return validation
        
        validation_data = validation.get('data', {})
        can_close = validation_data.get('canClose', False)
        missing = validation_data.get('missingArtifacts', [])
        
        # Si no puede cerrarse y no es forzado, retornar error
        if not can_close and not force_close:
            return {
                **ResponseMessage.message422,
                "data": "Cannot close project: missing mandatory artifacts",
                "missingArtifacts": missing
            }
        
        # Si es forzado, validar justificación
        if force_close and not justification:
            return {
                **ResponseMessage.message422,
                "data": "Justification required for forced closure"
            }
        
        # Buscar proyecto
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
        
        project_identifier = project.get('identifier')
        project_id_str = str(project['_id'])
        
        # Generar documento de cierre
        closure_doc = _generate_closure_document(
            project=project,
            user_id=user_id,
            force_close=force_close,
            justification=justification,
            closure_notes=closure_notes,
            missing_artifacts=missing,
            warnings=validation_data.get('warnings', [])
        )
        
        # Guardar documento de cierre como artefacto
        closure_artifact = {
            "projectId": project_identifier,
            "phase": "Transición",
            "artifactType": "Documento de Cierre",
            "filename": f"Cierre_{project_identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "filePath": None,
            "version": 1,
            "content": closure_doc,
            "observations": "Documento de cierre generado automáticamente",
            "fileType": "json",
            "author": user_id,
            "uploadDate": datetime.now().isoformat(),
            "isMandatory": True,
            "status": "Entregado",
            "tags": ["cierre", "automatico"],
            "createdAt": datetime.now()
        }
        
        dbConnLocal.clArtifacts.insert_one(closure_artifact)
        
        # Actualizar estado del proyecto a 'closed'
        update_data = {
            'status': 'closed',
            'closedAt': datetime.now(),
            'closedBy': user_id,
            'closureType': 'forced' if force_close else 'normal',
            'closureJustification': justification if force_close else None,
            'closureNotes': closure_notes
        }
        
        dbConnLocal.clProjects.update_one(
            {'_id': project['_id']},
            {'$set': update_data}
        )
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=user_id,
            action_type='close',
            entity_type='project',
            entity_id=project_id_str,
            details={
                'action': 'close_project',
                'forceClose': force_close,
                'justification': justification,
                'missingArtifactsCount': len(missing),
                'closureDocumentId': str(closure_artifact['_id']) if '_id' in closure_artifact else None
            },
            project_id=project_id_str
        )
        
        return {
            **ResponseMessage.message200,
            "data": {
                "projectId": project_id_str,
                "closureDocument": closure_doc,
                "closedAt": update_data['closedAt'].isoformat(),
                "closureType": update_data['closureType']
            },
            "message": "Project closed successfully"
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def _generate_closure_document(project, user_id, force_close, justification, 
                                closure_notes, missing_artifacts, warnings):
    """
    Genera documento de cierre con metadatos y enlaces a artefactos
    
    Returns:
        Dict con estructura del documento de cierre
    """
    project_identifier = project.get('identifier')
    
    # Obtener todos los artefactos del proyecto
    artifacts = list(dbConnLocal.clArtifacts.find({'projectId': project_identifier}))
    
    # Agrupar artefactos por fase
    artifacts_by_phase = {}
    for artifact in artifacts:
        phase = artifact.get('phase', 'Unknown')
        if phase not in artifacts_by_phase:
            artifacts_by_phase[phase] = []
        
        artifacts_by_phase[phase].append({
            'type': artifact.get('artifactType'),
            'version': artifact.get('version'),
            'status': artifact.get('status'),
            'author': artifact.get('author'),
            'uploadDate': artifact.get('uploadDate'),
            'filename': artifact.get('filename'),
            'filePath': artifact.get('filePath'),
            'externalLink': artifact.get('externalLink'),
            'isMandatory': artifact.get('isMandatory')
        })
    
    # Obtener información del usuario que cierra
    try:
        closing_user = dbConnLocal.clUsers.find_one({'_id': ObjectId(user_id)})
    except:
        closing_user = dbConnLocal.clUsers.find_one({'_id': user_id})
    
    closing_username = closing_user.get('username', user_id) if closing_user else user_id
    
    # Obtener miembros del proyecto
    members = list(dbConnLocal.clProjectMembers.find({
        'projectId': str(project['_id']),
        'status': 'active'
    }))
    
    team_summary = []
    for member in members:
        try:
            user = dbConnLocal.clUsers.find_one({'_id': ObjectId(member['userId'])})
        except:
            user = dbConnLocal.clUsers.find_one({'_id': member['userId']})
        
        if user:
            team_summary.append({
                'username': user.get('username'),
                'roles': member.get('roles', []),
                'joinedAt': member.get('acceptedAt').isoformat() if member.get('acceptedAt') else None
            })
    
    # Construir documento de cierre
    closure_doc = {
        'documentType': 'Documento de Cierre de Proyecto',
        'generatedAt': datetime.now().isoformat(),
        'generatedBy': closing_username,
        'project': {
            'id': str(project['_id']),
            'identifier': project_identifier,
            'name': project.get('name'),
            'description': project.get('description'),
            'startDate': project.get('startDate'),
            'endDate': datetime.now().isoformat(),
            'responsible': project.get('responsible'),
            'tags': project.get('tags', [])
        },
        'closureInfo': {
            'closureType': 'forced' if force_close else 'normal',
            'closedBy': closing_username,
            'closedAt': datetime.now().isoformat(),
            'justification': justification if force_close else None,
            'notes': closure_notes
        },
        'validation': {
            'missingMandatoryArtifacts': missing_artifacts,
            'warnings': warnings,
            'forcedClosure': force_close
        },
        'artifacts': artifacts_by_phase,
        'team': team_summary,
        'summary': {
            'totalArtifacts': len(artifacts),
            'totalPhases': len(project.get('phases', [])),
            'totalTeamMembers': len(team_summary),
            'projectDuration': _calculate_duration(
                project.get('startDate'),
                datetime.now().isoformat()
            )
        }
    }
    
    return closure_doc


def _calculate_duration(start_date, end_date):
    """
    Calcula duración del proyecto en días
    """
    try:
        from dateutil import parser
        start = parser.parse(start_date)
        end = parser.parse(end_date)
        delta = end - start
        return f"{delta.days} días"
    except:
        return "Unknown"


def fnGetClosureDocument(project_id):
    """
    Obtiene el documento de cierre de un proyecto
    
    Args:
        project_id: ID o identificador del proyecto
    
    Returns:
        Response con documento de cierre
    """
    try:
        # Buscar proyecto
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
        
        project_identifier = project.get('identifier')
        
        # Buscar documento de cierre
        closure_artifact = dbConnLocal.clArtifacts.find_one({
            'projectId': project_identifier,
            'artifactType': 'Documento de Cierre'
        }, sort=[('createdAt', -1)])
        
        if not closure_artifact:
            return {**ResponseMessage.message404, "data": "Closure document not found"}
        
        return {
            **ResponseMessage.message200,
            "data": {
                "closureDocument": closure_artifact.get('content'),
                "artifact": {
                    'id': str(closure_artifact['_id']),
                    'version': closure_artifact.get('version'),
                    'createdAt': closure_artifact.get('createdAt').isoformat() if closure_artifact.get('createdAt') else None,
                    'author': closure_artifact.get('author')
                }
            }
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnReopenProject(project_id, user_id, reason):
    """
    Reabre un proyecto cerrado (solo admin)
    
    Args:
        project_id: ID del proyecto
        user_id: ID del usuario (debe ser admin)
        reason: Razón para reabrir el proyecto
    
    Returns:
        Response con proyecto reabierto
    """
    try:
        if not reason or reason.strip() == "":
            return {**ResponseMessage.message422, "data": "Reason required to reopen project"}
        
        # Buscar proyecto
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
        
        if project.get('status') != 'closed':
            return {**ResponseMessage.message422, "data": "Project is not closed"}
        
        # Actualizar estado
        update_data = {
            'status': 'active',
            'reopenedAt': datetime.now(),
            'reopenedBy': user_id,
            'reopenReason': reason
        }
        
        dbConnLocal.clProjects.update_one(
            {'_id': project['_id']},
            {'$set': update_data}
        )
        
        # HU-024: Audit logging
        HelperFunctions.logAudit(
            user_id=user_id,
            action_type='edit',
            entity_type='project',
            entity_id=str(project['_id']),
            details={
                'action': 'reopen_project',
                'reason': reason
            },
            project_id=str(project['_id'])
        )
        
        return {
            **ResponseMessage.message200,
            "message": "Project reopened successfully"
        }
        
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGenerateClosurePDF(project_id):
    """
    Genera un PDF del documento de cierre con buena presentación
    
    Args:
        project_id: ID del proyecto
    
    Returns:
        BytesIO con el PDF generado
    """
    try:
        # Obtener documento de cierre
        result = fnGetClosureDocument(project_id)
        if result.get('intCode') != 200:
            return None
        
        closure_doc = result['data']['closureDocument']
        
        # Crear buffer para el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Contenedor para los elementos del PDF
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=8
        )
        
        normal_style = styles['Normal']
        
        # Título principal
        elements.append(Paragraph("Documento de Cierre de Proyecto", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Información del proyecto
        elements.append(Paragraph("Información del Proyecto", heading_style))
        
        project_info = closure_doc['project']
        project_data = [
            ['Campo', 'Valor'],
            ['Nombre', project_info['name']],
            ['Identificador', project_info['identifier']],
            ['Descripción', project_info.get('description', 'N/A')],
            ['Responsable', project_info.get('responsible', 'N/A')],
            ['Fecha Inicio', project_info.get('startDate', 'N/A')],
            ['Fecha Fin', project_info.get('endDate', 'N/A')],
        ]
        
        project_table = Table(project_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(project_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Información del cierre
        elements.append(Paragraph("Información del Cierre", heading_style))
        
        closure_info = closure_doc['closureInfo']
        closure_data = [
            ['Campo', 'Valor'],
            ['Tipo de Cierre', 'Forzado' if closure_info['closureType'] == 'forced' else 'Normal'],
            ['Cerrado Por', closure_info['closedBy']],
            ['Fecha de Cierre', closure_info['closedAt'][:19].replace('T', ' ')],
        ]
        
        if closure_info.get('justification'):
            closure_data.append(['Justificación', closure_info['justification']])
        
        if closure_info.get('notes'):
            closure_data.append(['Notas', closure_info['notes']])
        
        closure_table = Table(closure_data, colWidths=[2*inch, 4*inch])
        closure_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(closure_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Resumen del proyecto
        elements.append(Paragraph("Resumen", heading_style))
        
        summary = closure_doc['summary']
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Artefactos', str(summary['totalArtifacts'])],
            ['Total de Fases', str(summary['totalPhases'])],
            ['Total de Miembros', str(summary['totalTeamMembers'])],
            ['Duración del Proyecto', summary['projectDuration']],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Validación
        validation = closure_doc['validation']
        if validation['missingMandatoryArtifacts'] or validation['warnings']:
            elements.append(Paragraph("Estado de Validación", heading_style))
            
            if validation['forcedClosure']:
                elements.append(Paragraph(
                    "<b>ATENCIÓN:</b> Este proyecto se cerró de forma forzada.",
                    normal_style
                ))
                elements.append(Spacer(1, 0.1*inch))
            
            if validation['missingMandatoryArtifacts']:
                elements.append(Paragraph(f"Artefactos Faltantes: {len(validation['missingMandatoryArtifacts'])}", subheading_style))
                missing_data = [['Fase', 'Artefacto', 'Razón']]
                for item in validation['missingMandatoryArtifacts']:
                    missing_data.append([
                        item['phase'],
                        item['artifactType'],
                        'No encontrado' if item['reason'] == 'not_found' else 'No entregado'
                    ])
                
                missing_table = Table(missing_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
                missing_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                elements.append(missing_table)
                elements.append(Spacer(1, 0.2*inch))
            
            if validation['warnings']:
                elements.append(Paragraph(f"Advertencias: {len(validation['warnings'])}", subheading_style))
                warnings_data = [['Fase', 'Artefacto', 'Estado Actual']]
                for item in validation['warnings']:
                    warnings_data.append([
                        item['phase'],
                        item['artifactType'],
                        item['currentStatus']
                    ])
                
                warnings_table = Table(warnings_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
                warnings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                elements.append(warnings_table)
            
            elements.append(Spacer(1, 0.3*inch))
        
        # Nueva página para artefactos
        elements.append(PageBreak())
        elements.append(Paragraph("Artefactos del Proyecto", heading_style))
        
        # Artefactos por fase
        artifacts_by_phase = closure_doc['artifacts']
        for phase, artifacts in artifacts_by_phase.items():
            if not artifacts:
                continue
            
            elements.append(Paragraph(f"Fase: {phase}", subheading_style))
            
            artifact_data = [['Tipo', 'Versión', 'Estado', 'Autor']]
            for artifact in artifacts:
                artifact_data.append([
                    artifact['type'][:30],  # Truncar si es muy largo
                    f"v{artifact['version']}",
                    artifact['status'],
                    artifact['author'][:20]  # Truncar si es muy largo
                ])
            
            artifact_table = Table(artifact_data, colWidths=[2.5*inch, 0.8*inch, 1.2*inch, 1.5*inch])
            artifact_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(artifact_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Equipo del proyecto
        if closure_doc.get('team'):
            elements.append(PageBreak())
            elements.append(Paragraph("Equipo del Proyecto", heading_style))
            
            team_data = [['Usuario', 'Roles', 'Fecha de Ingreso']]
            for member in closure_doc['team']:
                team_data.append([
                    member['username'],
                    ', '.join(member['roles']),
                    member.get('joinedAt', 'N/A')[:10] if member.get('joinedAt') else 'N/A'
                ])
            
            team_table = Table(team_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
            team_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a085')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            
            elements.append(team_table)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"Documento generado el {closure_doc['generatedAt'][:19].replace('T', ' ')} por {closure_doc['generatedBy']}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )))
        
        # Construir PDF
        doc.build(elements)
        
        # Retornar buffer
        buffer.seek(0)
        return buffer
        
    except Exception:
        HelperFunctions.PrintException()
        return None

