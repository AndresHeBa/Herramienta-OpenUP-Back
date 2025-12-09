from flask import Blueprint, request
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
from BackEnd.Functions.buildFunctions import (
    fnRegisterBuild, 
    fnGetBuildsForArtifact, 
    fnGetBuildsForProject,
    fnLinkBuildToArtifact,
    fnUpdateBuildStatus,
    fnUpdateProjectRepository
)
from BackEnd.GlobalInfo.permissions import requireAction

# HU-022: Build management endpoints
buildBlueprint = Blueprint('builds', __name__)


@buildBlueprint.route('/api/builds/register', methods=['POST'])
@requireAction('register_build')
def registerBuild():
    """
    Register a new build for a project
    
    POST /api/builds/register
    Body: {
        "projectId": "string",
        "buildId": "string",
        "commitHash": "string (optional)",
        "buildDate": "datetime (optional)",
        "status": "string (optional, default: success)",
        "logs": "string (optional)",
        "metadata": "object (optional)",
        "artifactId": "string (optional)"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('projectId') or not data.get('buildId'):
            return {
                **ResponseMessage.message202,
                'data': 'projectId and buildId are required'
            }
        
        result = fnRegisterBuild(
            project_id=data['projectId'],
            build_id=data['buildId'],
            commit_hash=data.get('commitHash'),
            build_date=data.get('buildDate'),
            status=data.get('status', 'success'),
            logs=data.get('logs'),
            metadata=data.get('metadata'),
            artifact_id=data.get('artifactId'),
            user_id='system'
        )
        
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }


@buildBlueprint.route('/api/builds/artifact/<artifactId>', methods=['GET'])
@requireAction('view_builds')
def getBuildsForArtifact(artifactId):
    """
    Get all builds linked to an artifact
    
    GET /api/builds/artifact/<artifactId>
    """
    try:
        result = fnGetBuildsForArtifact(artifactId)
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }


@buildBlueprint.route('/api/builds/project/<projectId>', methods=['GET'])
@requireAction('view_builds')
def getBuildsForProject(projectId):
    """
    Get all builds for a project
    
    GET /api/builds/project/<projectId>
    """
    try:
        result = fnGetBuildsForProject(projectId)
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }


@buildBlueprint.route('/api/builds/<buildId>/link', methods=['PUT'])
@requireAction('link_build')
def linkBuildToArtifact(buildId):
    """
    Link an existing build to an artifact
    
    PUT /api/builds/<buildId>/link
    Body: {
        "artifactId": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('artifactId'):
            return {
                **ResponseMessage.message202,
                'data': 'artifactId is required'
            }
        
        result = fnLinkBuildToArtifact(
            build_id=buildId,
            artifact_id=data['artifactId'],
            user_id='system'
        )
        
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }


@buildBlueprint.route('/api/builds/<buildId>/status', methods=['PUT'])
@requireAction('update_build')
def updateBuildStatus(buildId):
    """
    Update build status
    
    PUT /api/builds/<buildId>/status
    Body: {
        "status": "string",
        "logs": "string (optional)"
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('status'):
            return {
                **ResponseMessage.message202,
                'data': 'status is required'
            }
        
        result = fnUpdateBuildStatus(
            build_id=buildId,
            status=data['status'],
            logs=data.get('logs'),
            user_id='system'
        )
        
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }


@buildBlueprint.route('/api/projects/<projectId>/repository', methods=['PUT'])
@requireAction('update_project')
def updateProjectRepository(projectId):
    """
    Update project repository information
    
    PUT /api/projects/<projectId>/repository
    Body: {
        "repositoryUrl": "string",
        "repositoryType": "string (optional, default: git)"
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('repositoryUrl'):
            return {
                **ResponseMessage.message202,
                'data': 'repositoryUrl is required'
            }
        
        result = fnUpdateProjectRepository(
            project_id=projectId,
            repository_url=data['repositoryUrl'],
            repository_type=data.get('repositoryType', 'git'),
            user_id='system'
        )
        
        return result
    
    except Exception as e:
        return {
            **ResponseMessage.message500,
            'data': str(e)
        }
