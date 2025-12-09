"""
Script to migrate existing system data to OpenUP configuration
Reads current roles, artifact types, and workflows from the database
and creates the initial configuration based on actual system data
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = HelperFunctions.dbConnection()


def migrate_existing_data_to_configuration():
    """Migrate existing system data to OpenUP configuration"""
    
    # Check if a configuration already exists
    existing = dbConnLocal.clConfigurations.find_one({})
    if existing:
        print("⚠️  Configuration already exists. Skipping migration.")
        print(f"   Existing configuration: {existing.get('name')}")
        response = input("   Do you want to create a new configuration anyway? (yes/no): ")
        if response.lower() not in ['yes', 'y', 'si', 's']:
            return
    
    print("\n🔄 Starting migration of existing data to OpenUP configuration...\n")
    
    # ========== MIGRATE ROLES ==========
    print("📋 Migrating roles...")
    roles = []
    existing_roles = list(dbConnLocal.clRoles.find())
    
    if existing_roles:
        for role in existing_roles:
            migrated_role = {
                "_id": str(role.get("_id", role.get("name", ""))),
                "name": role.get("displayName") or role.get("name", "Unknown Role"),
                "description": role.get("description", "Rol del sistema"),
                "responsibilities": []
            }
            roles.append(migrated_role)
        print(f"   ✅ Migrated {len(roles)} roles")
    else:
        print("   ⚠️  No roles found, using default roles")
        roles = get_default_roles()
    
    # ========== MIGRATE PHASES ==========
    print("\n📅 Setting up phases...")
    phases = get_default_phases()
    print(f"   ✅ Using {len(phases)} standard OpenUP phases")
    
    # ========== MIGRATE ARTIFACT TYPES ==========
    print("\n📄 Migrating artifact types...")
    artifact_types = []
    existing_artifacts = list(dbConnLocal.clArtifactTypes.find())
    
    if existing_artifacts:
        for artifact in existing_artifacts:
            migrated_artifact = {
                "_id": str(artifact.get("_id", "")),
                "name": artifact.get("artifactType") or artifact.get("name", "Unknown Artifact"),
                "description": artifact.get("description", "Tipo de artefacto del sistema"),
                "phase": artifact.get("phase", "Incepción"),
                "required": artifact.get("isMandatory", False),
                "customFields": []
            }
            artifact_types.append(migrated_artifact)
        print(f"   ✅ Migrated {len(artifact_types)} artifact types")
    else:
        print("   ⚠️  No artifact types found, using default types")
        artifact_types = get_default_artifacts()
    
    # ========== MIGRATE PERMISSIONS ==========
    print("\n🔐 Migrating permissions...")
    permissions = []
    existing_permissions = list(dbConnLocal.clPermissions.find())
    
    if existing_permissions:
        for perm in existing_permissions:
            migrated_permission = {
                "action": perm.get("action", ""),
                "roles": perm.get("roles", [])
            }
            permissions.append(migrated_permission)
        print(f"   ✅ Migrated {len(permissions)} permissions")
    else:
        print("   ⚠️  No permissions found, starting with empty permissions")
    
    # ========== MIGRATE WORKFLOWS ==========
    print("\n🔄 Migrating workflows...")
    workflows = []
    existing_workflows = list(dbConnLocal.clWorkflows.find())
    
    if existing_workflows:
        for workflow in existing_workflows:
            steps = []
            if workflow.get("states"):
                for idx, state in enumerate(workflow["states"]):
                    responsible = state.get("responsible", [])
                    if isinstance(responsible, list):
                        responsible_str = ", ".join(responsible) if responsible else "Sin asignar"
                    else:
                        responsible_str = str(responsible) if responsible else "Sin asignar"
                    
                    step = {
                        "name": state.get("name", f"Paso {idx + 1}"),
                        "order": idx + 1,
                        "description": f"Estado: {state.get('name', 'Sin descripción')}",
                        "responsibleRole": responsible_str
                    }
                    steps.append(step)
            
            migrated_workflow = {
                "_id": str(workflow.get("_id", "")),
                "name": workflow.get("name", "Flujo de Trabajo"),
                "description": f"Flujo migrado del sistema con {len(steps)} pasos",
                "steps": steps
            }
            workflows.append(migrated_workflow)
        print(f"   ✅ Migrated {len(workflows)} workflows")
    else:
        print("   ⚠️  No workflows found, using default workflows")
        workflows = get_default_workflows()
    
    # ========== CREATE CONFIGURATION ==========
    print("\n💾 Creating configuration...")
    
    migrated_config = {
        "version": 1,
        "name": "Configuración Migrada del Sistema",
        "description": "Configuración creada automáticamente a partir de los datos existentes en el sistema",
        "creationDate": datetime.utcnow(),
        "createdBy": "migration-script",
        "active": True,
        "roles": roles,
        "phases": phases,
        "artifactTypes": artifact_types,
        "workflows": workflows,
        "permissions": permissions
    }
    
    result = dbConnLocal.clConfigurations.insert_one(migrated_config)
    print(f"   ✅ Configuration created with ID: {result.inserted_id}")
    
    # ========== CREATE HISTORY ENTRY ==========
    history_entry = {
        "configurationId": str(result.inserted_id),
        "version": 1,
        "changeDate": datetime.utcnow(),
        "changedBy": "migration-script",
        "changeDescription": "Configuración inicial creada por migración automática de datos existentes",
        "previousConfiguration": migrated_config
    }
    dbConnLocal.clConfigurationHistory.insert_one(history_entry)
    print("   ✅ History entry created")
    
    # ========== SUMMARY ==========
    print("\n" + "="*60)
    print("✨ MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Configuration Summary:")
    print(f"   • Name: {migrated_config['name']}")
    print(f"   • Roles: {len(roles)}")
    print(f"   • Phases: {len(phases)}")
    print(f"   • Artifact Types: {len(artifact_types)}")
    print(f"   • Workflows: {len(workflows)}")
    print(f"   • Permissions: {len(permissions)}")
    print(f"   • Status: Active")
    print(f"   • Version: 1")
    print(f"\n🎯 Next steps:")
    print("   1. Access the admin configuration UI")
    print("   2. Review and customize the migrated configuration")
    print("   3. Add missing responsibilities, objectives, or custom fields")
    print("   4. Create additional configurations for different project types")
    print("\n")


def get_default_roles():
    """Returns default OpenUP roles if no roles exist in system"""
    return [
        {
            "_id": "role_stakeholder",
            "name": "Stakeholder",
            "description": "Persona o grupo con interés en el proyecto",
            "responsibilities": [
                "Proporcionar requisitos del negocio",
                "Revisar y aprobar entregables",
                "Participar en demostraciones"
            ]
        },
        {
            "_id": "role_analyst",
            "name": "Analista",
            "description": "Responsable de capturar y analizar requisitos",
            "responsibilities": [
                "Elicitar requisitos",
                "Crear casos de uso",
                "Documentar visión del proyecto"
            ]
        },
        {
            "_id": "role_developer",
            "name": "Desarrollador",
            "description": "Implementa el sistema",
            "responsibilities": [
                "Escribir código",
                "Realizar pruebas unitarias",
                "Integrar componentes"
            ]
        }
    ]


def get_default_phases():
    """Returns standard OpenUP phases"""
    return [
        {
            "_id": "phase_inception",
            "name": "Incepción",
            "description": "Establecer el alcance del proyecto y sus objetivos",
            "order": 1,
            "objectives": [
                "Comprender el problema a resolver",
                "Identificar stakeholders clave",
                "Definir el alcance del sistema",
                "Determinar la viabilidad del proyecto"
            ]
        },
        {
            "_id": "phase_elaboration",
            "name": "Elaboración",
            "description": "Establecer la arquitectura del sistema",
            "order": 2,
            "objectives": [
                "Definir arquitectura base",
                "Identificar y mitigar riesgos principales",
                "Refinar requisitos",
                "Estimar esfuerzo y calendario"
            ]
        },
        {
            "_id": "phase_construction",
            "name": "Construcción",
            "description": "Desarrollar el sistema de forma incremental",
            "order": 3,
            "objectives": [
                "Implementar funcionalidad completa",
                "Realizar pruebas exhaustivas",
                "Preparar documentación de usuario",
                "Alcanzar calidad suficiente para despliegue"
            ]
        },
        {
            "_id": "phase_transition",
            "name": "Transición",
            "description": "Transición del sistema a los usuarios",
            "order": 4,
            "objectives": [
                "Realizar pruebas beta",
                "Corregir defectos finales",
                "Capacitar usuarios",
                "Realizar despliegue en producción"
            ]
        }
    ]


def get_default_artifacts():
    """Returns default artifact types if none exist"""
    return [
        {
            "_id": "artifact_vision",
            "name": "Documento de Visión",
            "description": "Define la visión del proyecto y los requisitos de alto nivel",
            "phase": "Incepción",
            "required": True,
            "customFields": []
        },
        {
            "_id": "artifact_risks",
            "name": "Lista de Riesgos",
            "description": "Documenta los riesgos identificados del proyecto",
            "phase": "Incepción",
            "required": True,
            "customFields": []
        },
        {
            "_id": "artifact_architecture",
            "name": "Documento de Arquitectura",
            "description": "Documenta las decisiones arquitectónicas del sistema",
            "phase": "Elaboración",
            "required": True,
            "customFields": []
        }
    ]


def get_default_workflows():
    """Returns default workflows if none exist"""
    return [
        {
            "_id": "workflow_requirements",
            "name": "Gestión de Requisitos",
            "description": "Proceso para capturar y gestionar requisitos",
            "steps": [
                {
                    "name": "Identificar Stakeholders",
                    "order": 1,
                    "description": "Identificar todos los interesados",
                    "responsibleRole": "Analista"
                },
                {
                    "name": "Elicitar Requisitos",
                    "order": 2,
                    "description": "Capturar requisitos de stakeholders",
                    "responsibleRole": "Analista"
                },
                {
                    "name": "Revisar con Stakeholders",
                    "order": 3,
                    "description": "Validar requisitos capturados",
                    "responsibleRole": "Stakeholder"
                }
            ]
        }
    ]


if __name__ == "__main__":
    migrate_existing_data_to_configuration()
