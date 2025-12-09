from datetime import datetime
from bson import ObjectId
import json
import os
import zipfile
import tempfile
import shutil
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage

dbConnLocal = HelperFunctions.dbConnection()

# Custom JSON encoder for MongoDB types
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# HU-023: Export project with all artifacts and metadata
def fnExportProject(project_id, export_format='zip', include_files=True):
    """
    Export a complete project with all its data
    
    Args:
        project_id: Project ID to export
        export_format: 'zip' or 'json'
        include_files: Whether to include actual artifact files
    
    Returns:
        Response with file path or JSON data
    """
    try:
        if not ObjectId.is_valid(project_id):
            return {
                **ResponseMessage.message202,
                'data': 'invalid project id'
            }
        
        # Get project data
        project = dbConnLocal.clProjects.find_one({'_id': ObjectId(project_id)})
        if not project:
            return ResponseMessage.message404
        
        # Convert ObjectId to string for JSON serialization
        project['_id'] = str(project['_id'])
        if 'configuration_id' in project and project['configuration_id']:
            project['configuration_id'] = str(project['configuration_id'])
        
        # Get all artifacts for this project
        artifacts = list(dbConnLocal.clArtifacts.find({'projectId': project['identifier']}))
        for artifact in artifacts:
            artifact['_id'] = str(artifact['_id'])
        
        # Get all iterations
        iterations = list(dbConnLocal.clIteraciones.find({'projectId': project_id}))
        for iteration in iterations:
            iteration['_id'] = str(iteration['_id'])
            if 'projectId' in iteration:
                iteration['projectId'] = str(iteration['projectId'])
        
        # Get all microincrements
        microincrements = list(dbConnLocal.clMicroincrements.find({'projectId': project_id}))
        for micro in microincrements:
            micro['_id'] = str(micro['_id'])
            if 'projectId' in micro:
                micro['projectId'] = str(micro['projectId'])
        
        # Get project configuration if exists
        configuration = None
        if 'configuration_id' in project and project['configuration_id']:
            config_id = project['configuration_id']
            if config_id and config_id != 'null':
                configuration = dbConnLocal.clConfigurations.find_one({'_id': ObjectId(config_id)})
                if configuration:
                    configuration['_id'] = str(configuration['_id'])
        
        # Build export data
        export_data = {
            'exportDate': datetime.now().isoformat(),
            'exportVersion': '1.0',
            'project': project,
            'artifacts': artifacts,
            'iterations': iterations,
            'microincrements': microincrements,
            'configuration': configuration
        }
        
        if export_format == 'json':
            return {
                **ResponseMessage.message200,
                'Result': {
                    'format': 'json',
                    'data': export_data
                }
            }
        
        elif export_format == 'zip':
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.path.dirname(__file__), '..', 'Exports')
            os.makedirs(exports_dir, exist_ok=True)
            
            project_name = project.get('identifier', project_id)
            export_dirname = f"export_{project_name}"
            export_dir = os.path.join(exports_dir, export_dirname)
            
            # Remove old export if exists
            if os.path.exists(export_dir):
                shutil.rmtree(export_dir)
            os.makedirs(export_dir, exist_ok=True)
            
            # Write metadata JSON
            metadata_path = os.path.join(export_dir, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
            
            # Copy artifact files if requested
            if include_files:
                files_dir = os.path.join(export_dir, 'files')
                os.makedirs(files_dir, exist_ok=True)
                
                for artifact in artifacts:
                    if 'filePath' in artifact and artifact['filePath']:
                        src_path = artifact['filePath']
                        if os.path.exists(src_path):
                            try:
                                # Create phase directory
                                phase_dir = os.path.join(files_dir, artifact.get('phase', 'unknown'))
                                os.makedirs(phase_dir, exist_ok=True)
                                
                                # Copy file
                                filename = os.path.basename(src_path)
                                dst_path = os.path.join(phase_dir, f"{artifact.get('artifactType', 'artifact')}_{filename}")
                                shutil.copy2(src_path, dst_path)
                            except Exception as e:
                                print(f"Error copying file {src_path}: {e}")
            
            # Create ZIP file in exports directory
            zip_filename = f"export_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(exports_dir, zip_filename)
            
            # Remove old zip if exists
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            # Create ZIP with proper compression
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
                for root, dirs, files in os.walk(export_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join(export_dirname, os.path.relpath(file_path, export_dir))
                        zipf.write(file_path, arcname)
            
            # Verify ZIP was created successfully
            if not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
                return {
                    **ResponseMessage.message500,
                    'data': 'Failed to create ZIP file'
                }
            
            return {
                **ResponseMessage.message200,
                'Result': {
                    'format': 'zip',
                    'filePath': zip_path,
                    'filename': zip_filename,
                    'size': os.path.getsize(zip_path)
                }
            }
        
        else:
            return {
                **ResponseMessage.message202,
                'data': 'invalid export format'
            }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# HU-023: Import project template from JSON
def fnImportProjectTemplate(template_data, user_id='system'):
    """
    Import a project template and create a new project
    
    Args:
        template_data: JSON data containing project template
        user_id: User creating the project
    
    Returns:
        Response with created project ID
    """
    try:
        # Validate template data
        if 'project' not in template_data:
            return {
                **ResponseMessage.message202,
                'data': 'invalid template format: missing project data'
            }
        
        project_template = template_data['project']
        
        # Generate new identifier
        existing_count = dbConnLocal.clProjects.count_documents({})
        new_identifier = f"P-{str(existing_count + 1).zfill(3)}"
        
        # Create new project from template
        new_project = {
            'name': project_template.get('name', 'Imported Project'),
            'identifier': new_identifier,
            'startDate': project_template.get('startDate', datetime.now().isoformat()),
            'description': project_template.get('description', 'Imported from template'),
            'responsible': project_template.get('responsible', ''),
            'tags': project_template.get('tags', []),
            'phases': project_template.get('phases', []),
            'status': 'Creado',
            'active': True,
            'creationDate': datetime.now(),
            'modificationDate': datetime.now(),
            'createdBy': user_id
        }
        
        # Handle configuration
        if 'configuration' in template_data and template_data['configuration']:
            config = template_data['configuration']
            # Use existing configuration if active, or create new one
            existing_config = dbConnLocal.clConfigurations.find_one({
                'name': config.get('name'),
                'active': True
            })
            if existing_config:
                new_project['configuration_id'] = existing_config['_id']
            else:
                # Configuration will be handled separately or use default
                pass
        
        # Handle repository info
        if 'repositoryUrl' in project_template:
            new_project['repositoryUrl'] = project_template['repositoryUrl']
        if 'repositoryType' in project_template:
            new_project['repositoryType'] = project_template['repositoryType']
        
        # Insert project
        result = dbConnLocal.clProjects.insert_one(new_project)
        
        # Import iterations if present
        if 'iterations' in template_data:
            for iteration in template_data['iterations']:
                new_iteration = {
                    'projectId': str(result.inserted_id),
                    'name': iteration.get('name', ''),
                    'startDate': iteration.get('startDate', ''),
                    'endDate': iteration.get('endDate', ''),
                    'objectives': iteration.get('objectives', ''),
                    'status': 'Pendiente',
                    'createdAt': datetime.now()
                }
                dbConnLocal.clIteraciones.insert_one(new_iteration)
        
        return {
            **ResponseMessage.message200,
            'Result': {
                'projectId': str(result.inserted_id),
                'identifier': new_identifier,
                'message': 'Project imported successfully from template'
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# HU-023: Export project configuration/template
def fnExportConfiguration(config_id):
    """
    Export a configuration as a reusable template
    
    Args:
        config_id: Configuration ID to export
    
    Returns:
        Response with configuration data
    """
    try:
        if not ObjectId.is_valid(config_id):
            return {
                **ResponseMessage.message202,
                'data': 'invalid configuration id'
            }
        
        config = dbConnLocal.clConfigurations.find_one({'_id': ObjectId(config_id)})
        if not config:
            return ResponseMessage.message404
        
        # Convert ObjectId to string
        config['_id'] = str(config['_id'])
        
        export_data = {
            'exportDate': datetime.now().isoformat(),
            'exportVersion': '1.0',
            'type': 'configuration',
            'configuration': config
        }
        
        return {
            **ResponseMessage.message200,
            'Result': {
                'format': 'json',
                'data': export_data
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
