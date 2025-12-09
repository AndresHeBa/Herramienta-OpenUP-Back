from datetime import datetime
from bson import ObjectId
import BackEnd.GlobalInfo.Helpers as HelperFunctions
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage

# HU-022: Build management functions
dbConnLocal = HelperFunctions.dbConnection()

def fnRegisterBuild(project_id, build_id, commit_hash=None, build_date=None, status="success", 
                   logs=None, metadata=None, artifact_id=None, user_id=None):
    """
    Register a new build for a project, optionally linked to an artifact
    
    Args:
        project_id: Project ObjectId or identifier
        build_id: Build identifier from CI system
        commit_hash: Git commit hash
        build_date: Build execution date
        status: Build status (success, failure, pending, in_progress)
        logs: Build logs/output
        metadata: Additional build metadata (branch, trigger, etc)
        artifact_id: Optional artifact ID to link build to
        user_id: User who registered the build
    """
    try:
        # Find project by _id or identifier
        project = None
        if ObjectId.is_valid(project_id):
            project = dbConnLocal.clProjects.find_one({'_id': ObjectId(project_id)})
        if not project:
            project = dbConnLocal.clProjects.find_one({'identifier': project_id})
        
        if not project:
            return {
                **ResponseMessage.message404,
                'data': 'Project not found'
            }
        
        # Validate artifact if provided
        if artifact_id:
            if not ObjectId.is_valid(artifact_id):
                return {
                    **ResponseMessage.message202,
                    'data': 'Invalid artifact ID'
                }
            
            artifact = dbConnLocal.clArtifacts.find_one({'_id': ObjectId(artifact_id)})
            if not artifact:
                return {
                    **ResponseMessage.message404,
                    'data': 'Artifact not found'
                }
        
        # Create build document
        build = {
            "projectId": str(project['_id']),
            "buildId": build_id,
            "commitHash": commit_hash,
            "buildDate": build_date or datetime.now(),
            "status": status,
            "logs": logs,
            "metadata": metadata or {},
            "registeredBy": user_id,
            "registeredAt": datetime.now()
        }
        
        # Link to artifact if provided
        if artifact_id:
            build["artifactId"] = artifact_id
        
        # Remove blank attributes
        build = HelperFunctions.deleteBlankAttributes(build)
        
        # Insert build
        result = dbConnLocal.clBuilds.insert_one(build)
        
        print(f"Build registered: {build_id} for project {project['identifier']}")
        
        return {
            **ResponseMessage.message200,
            'data': {
                'buildId': str(result.inserted_id),
                'message': 'Build registered successfully'
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetBuildsForArtifact(artifact_id):
    """
    Get all builds linked to a specific artifact
    
    Args:
        artifact_id: Artifact ObjectId
    """
    try:
        if not ObjectId.is_valid(artifact_id):
            return {
                **ResponseMessage.message202,
                'data': 'Invalid artifact ID'
            }
        
        # Find all builds for this artifact
        builds = list(dbConnLocal.clBuilds.find({'artifactId': artifact_id}).sort('buildDate', -1))
        
        # Convert ObjectIds to strings
        for build in builds:
            build['_id'] = str(build['_id'])
        
        return {
            **ResponseMessage.message200,
            'Result': {
                'builds': builds,
                'count': len(builds)
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetBuildsForProject(project_id):
    """
    Get all builds for a project
    
    Args:
        project_id: Project ObjectId or identifier
    """
    try:
        # Find project
        project = None
        if ObjectId.is_valid(project_id):
            project = dbConnLocal.clProjects.find_one({'_id': ObjectId(project_id)})
        if not project:
            project = dbConnLocal.clProjects.find_one({'identifier': project_id})
        
        if not project:
            return {
                **ResponseMessage.message404,
                'data': 'Project not found'
            }
        
        # Find all builds for this project
        builds = list(dbConnLocal.clBuilds.find({'projectId': str(project['_id'])}).sort('buildDate', -1))
        
        # Convert ObjectIds to strings
        for build in builds:
            build['_id'] = str(build['_id'])
        
        return {
            **ResponseMessage.message200,
            'Result': {
                'builds': builds,
                'count': len(builds)
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnLinkBuildToArtifact(build_id, artifact_id, user_id=None):
    """
    Link an existing build to an artifact version
    
    Args:
        build_id: Build ObjectId
        artifact_id: Artifact ObjectId
        user_id: User performing the link
    """
    try:
        if not ObjectId.is_valid(build_id):
            return {
                **ResponseMessage.message202,
                'data': 'Invalid build ID'
            }
        
        if not ObjectId.is_valid(artifact_id):
            return {
                **ResponseMessage.message202,
                'data': 'Invalid artifact ID'
            }
        
        # Validate build exists
        build = dbConnLocal.clBuilds.find_one({'_id': ObjectId(build_id)})
        if not build:
            return {
                **ResponseMessage.message404,
                'data': 'Build not found'
            }
        
        # Validate artifact exists
        artifact = dbConnLocal.clArtifacts.find_one({'_id': ObjectId(artifact_id)})
        if not artifact:
            return {
                **ResponseMessage.message404,
                'data': 'Artifact not found'
            }
        
        # Update build with artifact link
        result = dbConnLocal.clBuilds.update_one(
            {'_id': ObjectId(build_id)},
            {
                '$set': {
                    'artifactId': artifact_id,
                    'linkedBy': user_id,
                    'linkedAt': datetime.now()
                }
            }
        )
        
        print(f"Build {build_id} linked to artifact {artifact_id}")
        
        return {
            **ResponseMessage.message200,
            'data': {
                'matched': result.matched_count,
                'modified': result.modified_count,
                'message': 'Build linked to artifact successfully'
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateBuildStatus(build_id, status, logs=None, user_id=None):
    """
    Update build status and optionally logs
    
    Args:
        build_id: Build ObjectId
        status: New status (success, failure, pending, in_progress)
        logs: Updated logs
        user_id: User performing the update
    """
    try:
        if not ObjectId.is_valid(build_id):
            return {
                **ResponseMessage.message202,
                'data': 'Invalid build ID'
            }
        
        # Validate build exists
        build = dbConnLocal.clBuilds.find_one({'_id': ObjectId(build_id)})
        if not build:
            return {
                **ResponseMessage.message404,
                'data': 'Build not found'
            }
        
        # Prepare update
        update_data = {
            'status': status,
            'updatedBy': user_id,
            'updatedAt': datetime.now()
        }
        
        if logs:
            update_data['logs'] = logs
        
        # Update build
        result = dbConnLocal.clBuilds.update_one(
            {'_id': ObjectId(build_id)},
            {'$set': update_data}
        )
        
        print(f"Build {build_id} status updated to {status}")
        
        return {
            **ResponseMessage.message200,
            'data': {
                'matched': result.matched_count,
                'modified': result.modified_count,
                'message': 'Build status updated successfully'
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateProjectRepository(project_id, repository_url, repository_type="git", user_id=None):
    """
    Update project repository information
    
    Args:
        project_id: Project ObjectId or identifier
        repository_url: Repository URL
        repository_type: Repository type (git, svn, etc)
        user_id: User performing the update
    """
    try:
        # Find project
        project = None
        if ObjectId.is_valid(project_id):
            project = dbConnLocal.clProjects.find_one({'_id': ObjectId(project_id)})
        if not project:
            project = dbConnLocal.clProjects.find_one({'identifier': project_id})
        
        if not project:
            return {
                **ResponseMessage.message404,
                'data': 'Project not found'
            }
        
        # Update repository info
        result = dbConnLocal.clProjects.update_one(
            {'_id': project['_id']},
            {
                '$set': {
                    'repositoryUrl': repository_url,
                    'repositoryType': repository_type,
                    'repositoryUpdatedBy': user_id,
                    'repositoryUpdatedAt': datetime.now()
                }
            }
        )
        
        print(f"Repository updated for project {project['identifier']}")
        
        return {
            **ResponseMessage.message200,
            'data': {
                'matched': result.matched_count,
                'modified': result.modified_count,
                'message': 'Repository information updated successfully'
            }
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
