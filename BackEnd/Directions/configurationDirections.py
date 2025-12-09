from flask import Blueprint, request
import BackEnd.Functions.configurationFunctions as confFunctions

configurationDirections = Blueprint("configurationDirections", __name__)


@configurationDirections.route("/api/configurations/active", methods=["GET"])
def getActiveConfiguration():
    """Get the active OpenUP configuration"""
    return confFunctions.fnGetActiveConfiguration()


@configurationDirections.route("/api/configurations", methods=["GET"])
def getConfigurations():
    """Get all configurations"""
    return confFunctions.fnGetConfigurations()


@configurationDirections.route("/api/configurations/<config_id>", methods=["GET"])
def getConfiguration(config_id):
    """Get a specific configuration"""
    return confFunctions.fnGetConfiguration(config_id)


@configurationDirections.route("/api/configurations", methods=["POST"])
def postConfiguration():
    """Create a new configuration"""
    data = request.json
    return confFunctions.fnPostConfiguration(
        data.get("name"),
        data.get("description"),
        data.get("createdBy")
    )


@configurationDirections.route("/api/configurations/<config_id>/activate", methods=["PUT"])
def setActiveConfiguration(config_id):
    """Set a configuration as active"""
    return confFunctions.fnSetActiveConfiguration(config_id)


@configurationDirections.route("/api/configurations/<config_id>/roles", methods=["POST"])
def addRole(config_id):
    """Add a role to a configuration"""
    data = request.json
    return confFunctions.fnAddRole(config_id, data)


@configurationDirections.route("/api/configurations/<config_id>/roles/<role_id>", methods=["PUT"])
def updateRole(config_id, role_id):
    """Update a role in a configuration"""
    data = request.json
    return confFunctions.fnUpdateRole(config_id, role_id, data)


@configurationDirections.route("/api/configurations/<config_id>/roles/<role_id>", methods=["DELETE"])
def deleteRole(config_id, role_id):
    """Delete a role from a configuration"""
    return confFunctions.fnDeleteRole(config_id, role_id)


# Phase endpoints
@configurationDirections.route("/api/configurations/<config_id>/phases", methods=["POST"])
def addPhase(config_id):
    """Add a phase to a configuration"""
    data = request.json
    return confFunctions.fnAddPhase(config_id, data)


@configurationDirections.route("/api/configurations/<config_id>/phases/<phase_id>", methods=["PUT"])
def updatePhase(config_id, phase_id):
    """Update a phase in a configuration"""
    data = request.json
    return confFunctions.fnUpdatePhase(config_id, phase_id, data)


@configurationDirections.route("/api/configurations/<config_id>/phases/<phase_id>", methods=["DELETE"])
def deletePhase(config_id, phase_id):
    """Delete a phase from a configuration"""
    return confFunctions.fnDeletePhase(config_id, phase_id)


# Artifact Type endpoints
@configurationDirections.route("/api/configurations/<config_id>/artifact-types", methods=["POST"])
def addArtifactType(config_id):
    """Add an artifact type to a configuration"""
    data = request.json
    return confFunctions.fnAddArtifactType(config_id, data)


@configurationDirections.route("/api/configurations/<config_id>/artifact-types/<artifact_id>", methods=["PUT"])
def updateArtifactType(config_id, artifact_id):
    """Update an artifact type in a configuration"""
    data = request.json
    return confFunctions.fnUpdateArtifactType(config_id, artifact_id, data)


@configurationDirections.route("/api/configurations/<config_id>/artifact-types/<artifact_id>", methods=["DELETE"])
def deleteArtifactType(config_id, artifact_id):
    """Delete an artifact type from a configuration"""
    return confFunctions.fnDeleteArtifactType(config_id, artifact_id)


# Workflow endpoints
@configurationDirections.route("/api/configurations/<config_id>/workflows", methods=["POST"])
def addWorkflow(config_id):
    """Add a workflow to a configuration"""
    data = request.json
    return confFunctions.fnAddWorkflow(config_id, data)


@configurationDirections.route("/api/configurations/<config_id>/workflows/<workflow_id>", methods=["PUT"])
def updateWorkflow(config_id, workflow_id):
    """Update a workflow in a configuration"""
    data = request.json
    return confFunctions.fnUpdateWorkflow(config_id, workflow_id, data)


@configurationDirections.route("/api/configurations/<config_id>/workflows/<workflow_id>", methods=["DELETE"])
def deleteWorkflow(config_id, workflow_id):
    """Delete a workflow from a configuration"""
    return confFunctions.fnDeleteWorkflow(config_id, workflow_id)


@configurationDirections.route("/api/configurations/<config_id>/history", methods=["GET"])
def getConfigurationHistory(config_id):
    """Get configuration change history"""
    return confFunctions.fnGetConfigurationHistory(config_id)


@configurationDirections.route("/api/configurations/<config_id>/revert/<int:version>", methods=["POST"])
def revertToVersion(config_id, version):
    """Revert configuration to a previous version"""
    return confFunctions.fnRevertToVersion(config_id, version)


@configurationDirections.route("/api/configurations/applyToAllProjects", methods=["POST"])
def applyToAllProjects():
    """Apply configuration to all existing projects"""
    data = request.json
    config_id = data.get("configId")
    if not config_id:
        return {"status": 422, "message": "configId is required"}, 422
    return confFunctions.fnApplyConfigurationToAllProjects(config_id)


@configurationDirections.route("/api/configurations/<config_id>/permissions", methods=["PUT"])
def updatePermissions(config_id):
    """Update permissions in a configuration"""
    data = request.json
    permissions = data.get("permissions")
    if not permissions:
        return {"status": 422, "message": "permissions is required"}, 422
    return confFunctions.fnUpdatePermissions(config_id, permissions)


@configurationDirections.route("/api/configurations/project/<project_id>", methods=["GET"])
def getProjectConfiguration(project_id):
    """Get the configuration associated with a specific project"""
    return confFunctions.fnGetProjectConfiguration(project_id)
