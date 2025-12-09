from flask import Blueprint, request, send_file
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
from BackEnd.Functions.exportImportFunctions import (
    fnExportProject,
    fnImportProjectTemplate,
    fnExportConfiguration
)
from BackEnd.GlobalInfo.permissions import requireAction

# HU-023: Export/Import endpoints
exportImportBlueprint = Blueprint('exportImport', __name__)


@exportImportBlueprint.route('/api/export/project/<projectId>', methods=['GET'])
@requireAction('export_project')
def exportProject(projectId):
    """
    Export a project with all its data
    
    GET /api/export/project/<projectId>?format=zip&includeFiles=true
    
    Query params:
        - format: 'zip' or 'json' (default: 'zip')
        - includeFiles: 'true' or 'false' (default: 'true')
    """
    try:
        export_format = request.args.get('format', 'zip')
        include_files = request.args.get('includeFiles', 'true').lower() == 'true'
        
        result = fnExportProject(projectId, export_format, include_files)
        
        # If ZIP format, send file for download
        if result.get('intCode') == 200 and export_format == 'zip':
            file_path = result['Result']['filePath']
            filename = result['Result']['filename']
            
            # Verify file exists and is readable
            import os
            if not os.path.exists(file_path):
                return {
                    **ResponseMessage.message500,
                    'data': 'Export file not found'
                }
            
            print(f"Sending file: {file_path} (size: {os.path.getsize(file_path)} bytes)")
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/zip',
                conditional=False
            )
        
        return result
    
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }


@exportImportBlueprint.route('/api/import/project', methods=['POST'])
@requireAction('create')
def importProject():
    """
    Import a project from template
    
    POST /api/import/project
    Body: {
        "templateData": {...}, // JSON template data
        "file": <file> // Optional: uploaded JSON file
    }
    """
    try:
        # Check if file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return {
                    **ResponseMessage.message202,
                    'data': 'no file selected'
                }
            
            # Read and parse JSON from file
            import json
            template_data = json.load(file)
        else:
            # Get JSON from request body
            data = request.get_json()
            if not data or 'templateData' not in data:
                return {
                    **ResponseMessage.message202,
                    'data': 'templateData is required'
                }
            template_data = data['templateData']
        
        # Get user ID from session/header (simplified for now)
        user_id = 'system'
        
        result = fnImportProjectTemplate(template_data, user_id)
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }


@exportImportBlueprint.route('/api/export/configuration/<configId>', methods=['GET'])
@requireAction('view')
def exportConfiguration(configId):
    """
    Export a configuration as template
    
    GET /api/export/configuration/<configId>
    """
    try:
        result = fnExportConfiguration(configId)
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }
