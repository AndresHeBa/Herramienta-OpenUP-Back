from datetime import datetime
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions
from bson.objectid import ObjectId

dbConnLocal = HelperFunctions.dbConnection()


def fnGetActiveConfiguration():
    """Get the active OpenUP configuration"""
    try:
        config = dbConnLocal.clConfigurations.find_one({"active": True})
        
        if not config:
            return ResponseMessage.message404
        
        config["_id"] = str(config["_id"])
        
        return {
            **ResponseMessage.message200,
            "data": config
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetConfigurations():
    """Get all configurations"""
    try:
        configs = list(dbConnLocal.clConfigurations.find())
        
        for config in configs:
            config["_id"] = str(config["_id"])
        
        return {
            **ResponseMessage.message200,
            "data": configs
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetConfiguration(config_id):
    """Get a specific configuration by ID"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        
        if not config:
            return ResponseMessage.message404
        
        config["_id"] = str(config["_id"])
        
        return {
            **ResponseMessage.message200,
            "data": config
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnPostConfiguration(name, description, created_by):
    """Create a new configuration"""
    try:
        # Check if there are any existing configurations
        existing_count = dbConnLocal.clConfigurations.count_documents({})
        
        new_config = {
            "version": 1,
            "name": name,
            "description": description,
            "creationDate": datetime.utcnow(),
            "createdBy": created_by,
            "roles": [],
            "phases": [],
            "artifactTypes": [],
            "workflows": [],
            "permissions": [],
            "active": existing_count == 0  # First configuration is active by default
        }
        
        result = dbConnLocal.clConfigurations.insert_one(new_config)
        
        return {
            **ResponseMessage.message201,
            "data": {"_id": str(result.inserted_id)}
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnSetActiveConfiguration(config_id):
    """Set a configuration as active"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        # Deactivate all configurations
        dbConnLocal.clConfigurations.update_many({}, {"$set": {"active": False}})
        
        # Activate the selected one
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {"$set": {"active": True}}
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        # Get activated configuration
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        
        # Sync to legacy collections for backward compatibility
        sync_to_legacy_collections(config)
        
        # Save to history
        fnSaveConfigurationHistory(config_id, config, "Set as active configuration", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnAddRole(config_id, role_data):
    """Add a role to a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        role_data["_id"] = str(ObjectId())
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$push": {"roles": role_data},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        # Save to history
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Added role: {role_data['name']}", config.get("createdBy", "system"))
        
        return ResponseMessage.message201
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateRole(config_id, role_id, role_data):
    """Update a role in a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        update_fields = {}
        for key, value in role_data.items():
            if key != "_id":
                update_fields[f"roles.$.{key}"] = value
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id), "roles._id": role_id},
            {
                "$set": update_fields,
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        # Save to history
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Updated role: {role_data.get('name', role_id)}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnDeleteRole(config_id, role_id):
    """Delete a role from a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$pull": {"roles": {"_id": role_id}},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        # Save to history
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Deleted role: {role_id}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnAddPhase(config_id, phase_data):
    """Add a phase to a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        phase_data["_id"] = str(ObjectId())
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$push": {"phases": phase_data},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Added phase: {phase_data['name']}", config.get("createdBy", "system"))
        
        return ResponseMessage.message201
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdatePhase(config_id, phase_id, phase_data):
    """Update a phase in a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        update_fields = {}
        for key, value in phase_data.items():
            if key != "_id":
                update_fields[f"phases.$.{key}"] = value
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id), "phases._id": phase_id},
            {
                "$set": update_fields,
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Updated phase: {phase_data.get('name', phase_id)}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnDeletePhase(config_id, phase_id):
    """Delete a phase from a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$pull": {"phases": {"_id": phase_id}},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Deleted phase: {phase_id}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnAddArtifactType(config_id, artifact_data):
    """Add an artifact type to a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        artifact_data["_id"] = str(ObjectId())
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$push": {"artifactTypes": artifact_data},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Added artifact type: {artifact_data['name']}", config.get("createdBy", "system"))
        
        return ResponseMessage.message201
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateArtifactType(config_id, artifact_id, artifact_data):
    """Update an artifact type in a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        update_fields = {}
        for key, value in artifact_data.items():
            if key != "_id":
                update_fields[f"artifactTypes.$.{key}"] = value
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id), "artifactTypes._id": artifact_id},
            {
                "$set": update_fields,
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Updated artifact type: {artifact_data.get('name', artifact_id)}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnDeleteArtifactType(config_id, artifact_id):
    """Delete an artifact type from a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$pull": {"artifactTypes": {"_id": artifact_id}},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Deleted artifact type: {artifact_id}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnAddWorkflow(config_id, workflow_data):
    """Add a workflow to a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        workflow_data["_id"] = str(ObjectId())
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$push": {"workflows": workflow_data},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Added workflow: {workflow_data['name']}", config.get("createdBy", "system"))
        
        return ResponseMessage.message201
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnUpdateWorkflow(config_id, workflow_id, workflow_data):
    """Update a workflow in a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        update_fields = {}
        for key, value in workflow_data.items():
            if key != "_id":
                update_fields[f"workflows.$.{key}"] = value
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id), "workflows._id": workflow_id},
            {
                "$set": update_fields,
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Updated workflow: {workflow_data.get('name', workflow_id)}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnDeleteWorkflow(config_id, workflow_id):
    """Delete a workflow from a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$pull": {"workflows": {"_id": workflow_id}},
                "$inc": {"version": 1}
            }
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, config, f"Deleted workflow: {workflow_id}", config.get("createdBy", "system"))
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnSaveConfigurationHistory(config_id, config, change_description, changed_by):
    """Save configuration change to history"""
    try:
        history_entry = {
            "configurationId": str(config_id),
            "version": config.get("version", 1),
            "changeDate": datetime.utcnow(),
            "changedBy": changed_by,
            "changeDescription": change_description,
            "previousConfiguration": config
        }
        
        dbConnLocal.clConfigurationHistory.insert_one(history_entry)
        
    except Exception:
        HelperFunctions.PrintException()


def fnGetConfigurationHistory(config_id):
    """Get configuration change history"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        # Try both string and ObjectId formats for configurationId
        history = list(dbConnLocal.clConfigurationHistory.find({
            "$or": [
                {"configurationId": config_id},
                {"configurationId": ObjectId(config_id)}
            ]
        }).sort("changeDate", -1).limit(50))
        
        for entry in history:
            entry["_id"] = str(entry["_id"])
            if "configurationId" in entry and isinstance(entry["configurationId"], ObjectId):
                entry["configurationId"] = str(entry["configurationId"])
            if "previousConfiguration" in entry and "_id" in entry["previousConfiguration"]:
                entry["previousConfiguration"]["_id"] = str(entry["previousConfiguration"]["_id"])
        
        return {
            **ResponseMessage.message200,
            "data": history
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnRevertToVersion(config_id, version):
    """Revert configuration to a previous version"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        # Find the version in history - try both string and ObjectId
        history_entry = dbConnLocal.clConfigurationHistory.find_one({
            "$or": [
                {"configurationId": config_id, "version": version},
                {"configurationId": ObjectId(config_id), "version": version}
            ]
        })
        
        if not history_entry or "previousConfiguration" not in history_entry:
            return ResponseMessage.message404
        
        previous_config = history_entry["previousConfiguration"]
        previous_config["_id"] = ObjectId(config_id)
        previous_config["version"] = previous_config.get("version", 1) + 1
        
        # Save current as history before reverting
        current = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        fnSaveConfigurationHistory(config_id, current, f"Reverted to version {version}", current.get("createdBy", "system"))
        
        # Replace with previous version
        dbConnLocal.clConfigurations.replace_one(
            {"_id": ObjectId(config_id)},
            previous_config
        )
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


# ==================== ADAPTER FUNCTIONS ====================

def fnGetRolesFromActiveConfig():
    """Adapter: Returns roles from active config in the same format as clRoles"""
    try:
        config = dbConnLocal.clConfigurations.find_one({"active": True})
        
        if not config:
            # Fallback to old collection
            return list(dbConnLocal.clRoles.find())
        
        # Transform config roles to old format
        roles = []
        for role in config.get("roles", []):
            roles.append({
                "_id": role.get("_id"),
                "name": role.get("name"),
                "displayName": role.get("name"),
                "description": role.get("description"),
                "responsibilities": role.get("responsibilities", [])
            })
        
        return roles
    except Exception:
        HelperFunctions.PrintException()
        return list(dbConnLocal.clRoles.find())


def fnGetArtifactTypesFromActiveConfig():
    """Adapter: Returns artifact types from active config"""
    try:
        config = dbConnLocal.clConfigurations.find_one({"active": True})
        
        if not config:
            return list(dbConnLocal.clArtifactTypes.find())
        
        artifacts = []
        for artifact in config.get("artifactTypes", []):
            artifacts.append({
                "_id": artifact.get("_id"),
                "artifactType": artifact.get("name"),
                "name": artifact.get("name"),
                "description": artifact.get("description"),
                "phase": artifact.get("phase"),
                "isMandatory": artifact.get("required", False)
            })
        
        return artifacts
    except Exception:
        HelperFunctions.PrintException()
        return list(dbConnLocal.clArtifactTypes.find())


def fnGetWorkflowsFromActiveConfig():
    """Adapter: Returns workflows from active config"""
    try:
        config = dbConnLocal.clConfigurations.find_one({"active": True})
        
        if not config:
            return list(dbConnLocal.clWorkflows.find({"isActive": True}))
        
        workflows = []
        for wf in config.get("workflows", []):
            # Convert steps to states format
            states = []
            for step in wf.get("steps", []):
                states.append({
                    "name": step.get("name"),
                    "responsible": step.get("responsibleRole", "")
                })
            
            workflows.append({
                "_id": wf.get("_id"),
                "name": wf.get("name"),
                "description": wf.get("description"),
                "states": states,
                "isActive": True
            })
        
        return workflows
    except Exception:
        HelperFunctions.PrintException()
        return list(dbConnLocal.clWorkflows.find({"isActive": True}))


def fnGetPermissionsFromActiveConfig():
    """Adapter: Returns permissions from active config"""
    try:
        config = dbConnLocal.clConfigurations.find_one({"active": True})
        
        if not config:
            return list(dbConnLocal.clPermissions.find())
        
        # Return permissions from config
        permissions = config.get("permissions", [])
        return permissions
    except Exception:
        HelperFunctions.PrintException()
        return list(dbConnLocal.clPermissions.find())


# ==================== SYNC TO LEGACY COLLECTIONS ====================

def sync_to_legacy_collections(config):
    """Sync active configuration to legacy collections for backward compatibility"""
    try:
        # Sync roles
        dbConnLocal.clRoles.delete_many({})
        for role in config.get("roles", []):
            dbConnLocal.clRoles.insert_one({
                "name": role["name"],
                "displayName": role["name"],
                "description": role.get("description", "")
            })
        
        # Sync artifact types
        dbConnLocal.clArtifactTypes.delete_many({})
        for artifact in config.get("artifactTypes", []):
            dbConnLocal.clArtifactTypes.insert_one({
                "artifactType": artifact["name"],
                "name": artifact["name"],
                "description": artifact.get("description", ""),
                "phase": artifact.get("phase", "Incepción"),
                "isMandatory": artifact.get("required", False)
            })
        
        # Sync workflows
        dbConnLocal.clWorkflows.update_many({}, {"$set": {"isActive": False}})
        for wf in config.get("workflows", []):
            states = []
            for step in wf.get("steps", []):
                states.append({
                    "name": step["name"],
                    "responsible": step.get("responsibleRole", "")
                })
            
            existing = dbConnLocal.clWorkflows.find_one({"name": wf["name"]})
            if existing:
                dbConnLocal.clWorkflows.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "description": wf.get("description", ""),
                        "states": states,
                        "isActive": True
                    }}
                )
            else:
                dbConnLocal.clWorkflows.insert_one({
                    "name": wf["name"],
                    "description": wf.get("description", ""),
                    "states": states,
                    "isActive": True
                })
        
        # Sync permissions
        dbConnLocal.clPermissions.delete_many({})
        for permission in config.get("permissions", []):
            dbConnLocal.clPermissions.insert_one({
                "action": permission.get("action"),
                "roles": permission.get("roles", [])
            })
        
        print(f"✅ Synced {len(config.get('roles', []))} roles, {len(config.get('artifactTypes', []))} artifacts, {len(config.get('workflows', []))} workflows, {len(config.get('permissions', []))} permissions to legacy collections")
        
    except Exception:
        HelperFunctions.PrintException()
        raise


# ==================== APPLY TO PROJECTS ====================

def fnApplyConfigurationToAllProjects(config_id):
    """Apply active configuration to all existing projects"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        if not config:
            return ResponseMessage.message404
        
        # Get all projects
        projects = list(dbConnLocal.clProjects.find())
        updated_count = 0
        
        for project in projects:
            updates = {}
            
            # Map team roles to new configuration
            if "team" in project and project["team"]:
                new_team = []
                for member in project["team"]:
                    old_role = member.get("role", "")
                    # Try to find equivalent role in new config
                    new_role = find_equivalent_role(old_role, config.get("roles", []))
                    member["role"] = new_role
                    new_team.append(member)
                updates["team"] = new_team
            
            # Update project phases if needed
            if "phase" in project:
                old_phase = project["phase"]
                # Validate phase exists in new config
                valid_phases = [p["name"] for p in config.get("phases", [])]
                if old_phase not in valid_phases and valid_phases:
                    updates["phase"] = valid_phases[0]  # Default to first phase
            
            # Apply updates if any
            if updates:
                dbConnLocal.clProjects.update_one(
                    {"_id": project["_id"]},
                    {"$set": updates}
                )
                updated_count += 1
        
        return {
            **ResponseMessage.message200,
            "message": f"Configuration applied to {updated_count} projects",
            "updatedCount": updated_count
        }
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def find_equivalent_role(old_role, new_roles):
    """Find equivalent role in new configuration"""
    # Direct match
    for role in new_roles:
        if role["name"].lower() == old_role.lower():
            return role["name"]
    
    # Fuzzy match (contains)
    for role in new_roles:
        if old_role.lower() in role["name"].lower() or role["name"].lower() in old_role.lower():
            return role["name"]
    
    # Default to first role or original
    return new_roles[0]["name"] if new_roles else old_role


# ==================== UPDATE PERMISSIONS ====================

def fnUpdatePermissions(config_id, permissions):
    """Update permissions in a configuration"""
    try:
        if not ObjectId.is_valid(config_id):
            return ResponseMessage.message422
        
        # Validate permissions structure
        if not isinstance(permissions, list):
            return {**ResponseMessage.message422, "message": "Permissions must be an array"}
        
        for perm in permissions:
            if not isinstance(perm, dict) or "action" not in perm or "roles" not in perm:
                return {**ResponseMessage.message422, "message": "Each permission must have 'action' and 'roles'"}
        
        # Update permissions in configuration
        result = dbConnLocal.clConfigurations.update_one(
            {"_id": ObjectId(config_id)},
            {"$set": {"permissions": permissions}}
        )
        
        if result.matched_count == 0:
            return ResponseMessage.message404
        
        # Get updated configuration
        config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        
        # If this is the active configuration, sync to legacy collection
        if config.get("active"):
            dbConnLocal.clPermissions.delete_many({})
            for permission in permissions:
                dbConnLocal.clPermissions.insert_one({
                    "action": permission.get("action"),
                    "roles": permission.get("roles", [])
                })
        
        # Save to history
        fnSaveConfigurationHistory(
            config_id, 
            config, 
            "Updated permissions", 
            config.get("createdBy", "system")
        )
        
        return ResponseMessage.message200
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetProjectConfiguration(project_id):
    """Get the configuration associated with a specific project"""
    try:
        print(f"🔍 Getting configuration for project: {project_id}")
        
        # Try to find project by _id first (if it's a valid ObjectId)
        project = None
        if ObjectId.is_valid(project_id):
            project = dbConnLocal.clProjects.find_one({"_id": ObjectId(project_id)})
            print(f"   Searched by ObjectId: {'Found' if project else 'Not found'}")
        
        # If not found, try to find by identifier (e.g., "P-001")
        if not project:
            project = dbConnLocal.clProjects.find_one({"identifier": project_id})
            print(f"   Searched by identifier: {'Found' if project else 'Not found'}")
        
        if not project:
            print(f"   ❌ Project not found")
            return ResponseMessage.message404
        
        print(f"   ✅ Project found: {project.get('name', 'Unknown')}")
        
        # Get configuration ID from project
        config_id = project.get("configurationId")
        print(f"   Configuration ID in project: {config_id}")
        
        if not config_id:
            # If no configuration is set, return the active configuration
            print(f"   ⚠️ No configurationId, returning active configuration")
            return fnGetActiveConfiguration()
        
        # Get the specific configuration
        if ObjectId.is_valid(config_id):
            config = dbConnLocal.clConfigurations.find_one({"_id": ObjectId(config_id)})
        else:
            config = dbConnLocal.clConfigurations.find_one({"_id": config_id})
        
        if not config:
            # Fallback to active configuration if project's config not found
            print(f"   ⚠️ Configuration not found, returning active configuration")
            return fnGetActiveConfiguration()
        
        config["_id"] = str(config["_id"])
        print(f"   ✅ Returning configuration: {config.get('name', 'Unknown')} v{config.get('version', '?')}")
        
        return {
            **ResponseMessage.message200,
            "data": config
        }
    
    except Exception:
        print(f"   ❌ Exception in fnGetProjectConfiguration")
        HelperFunctions.PrintException()
        return ResponseMessage.message500
