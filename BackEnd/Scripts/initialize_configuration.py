"""
Script to initialize the default OpenUP configuration in MongoDB
Run this script once to create the initial configuration
"""

from datetime import datetime
import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = HelperFunctions.dbConnection()

def initialize_default_configuration():
    """Initialize the database with the default OpenUP configuration"""
    
    # Check if a configuration already exists
    existing = dbConnLocal.clConfigurations.find_one({})
    if existing:
        print("Configuration already exists. Skipping initialization.")
        return
    
    default_config = {
        "version": 1,
        "name": "OpenUP Estándar",
        "description": "Configuración estándar de OpenUP con roles, fases, artefactos y flujos predefinidos",
        "creationDate": datetime.utcnow(),
        "createdBy": "system",
        "active": True,
        
        "roles": [
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
                "_id": "role_architect",
                "name": "Arquitecto",
                "description": "Define la arquitectura del sistema",
                "responsibilities": [
                    "Diseñar arquitectura del sistema",
                    "Tomar decisiones técnicas",
                    "Documentar arquitectura"
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
            },
            {
                "_id": "role_tester",
                "name": "Probador",
                "description": "Verifica la calidad del sistema",
                "responsibilities": [
                    "Diseñar casos de prueba",
                    "Ejecutar pruebas",
                    "Reportar defectos"
                ]
            },
            {
                "_id": "role_project_manager",
                "name": "Gestor de Proyecto",
                "description": "Gestiona el proyecto",
                "responsibilities": [
                    "Planificar iteraciones",
                    "Gestionar riesgos",
                    "Coordinar equipo"
                ]
            }
        ],
        
        "phases": [
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
        ],
        
        "artifactTypes": [
            {
                "_id": "artifact_vision",
                "name": "Documento de Visión",
                "description": "Define la visión del proyecto y los requisitos de alto nivel",
                "phase": "Incepción",
                "required": True,
                "customFields": [
                    {
                        "name": "Audiencia Objetivo",
                        "type": "text",
                        "required": True
                    },
                    {
                        "name": "Características Principales",
                        "type": "textarea",
                        "required": True
                    }
                ]
            },
            {
                "_id": "artifact_stakeholders",
                "name": "Lista de Stakeholders",
                "description": "Identifica todos los interesados en el proyecto",
                "phase": "Incepción",
                "required": True,
                "customFields": []
            },
            {
                "_id": "artifact_risks",
                "name": "Lista de Riesgos Iniciales",
                "description": "Documenta los riesgos identificados del proyecto",
                "phase": "Incepción",
                "required": True,
                "customFields": [
                    {
                        "name": "Nivel de Impacto",
                        "type": "select",
                        "options": ["Alto", "Medio", "Bajo"],
                        "required": True
                    },
                    {
                        "name": "Probabilidad",
                        "type": "select",
                        "options": ["Alta", "Media", "Baja"],
                        "required": True
                    }
                ]
            },
            {
                "_id": "artifact_use_cases",
                "name": "Modelo de Casos de Uso de Alto Nivel",
                "description": "Representa los casos de uso principales del sistema",
                "phase": "Incepción",
                "required": True,
                "customFields": []
            },
            {
                "_id": "artifact_project_plan",
                "name": "Plan de Proyecto",
                "description": "Plan general del proyecto incluyendo calendario y recursos",
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
                "customFields": [
                    {
                        "name": "Estilo Arquitectónico",
                        "type": "text",
                        "required": True
                    }
                ]
            },
            {
                "_id": "artifact_detailed_use_cases",
                "name": "Especificación Detallada de Casos de Uso",
                "description": "Describe los casos de uso en detalle",
                "phase": "Elaboración",
                "required": True,
                "customFields": []
            },
            {
                "_id": "artifact_design_model",
                "name": "Modelo de Diseño",
                "description": "Modelo detallado del diseño del sistema",
                "phase": "Elaboración",
                "required": False,
                "customFields": []
            },
            {
                "_id": "artifact_source_code",
                "name": "Código Fuente",
                "description": "Implementación del sistema",
                "phase": "Construcción",
                "required": True,
                "customFields": []
            },
            {
                "_id": "artifact_test_cases",
                "name": "Casos de Prueba",
                "description": "Casos de prueba para validar el sistema",
                "phase": "Construcción",
                "required": True,
                "customFields": []
            },
            {
                "_id": "artifact_user_manual",
                "name": "Manual de Usuario",
                "description": "Documentación para usuarios finales",
                "phase": "Transición",
                "required": True,
                "customFields": []
            },
            {
                "_id": "artifact_deployment_guide",
                "name": "Guía de Despliegue",
                "description": "Instrucciones para desplegar el sistema",
                "phase": "Transición",
                "required": True,
                "customFields": []
            }
        ],
        
        "workflows": [
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
                        "name": "Documentar Visión",
                        "order": 3,
                        "description": "Crear documento de visión",
                        "responsibleRole": "Analista"
                    },
                    {
                        "name": "Revisar con Stakeholders",
                        "order": 4,
                        "description": "Validar requisitos capturados",
                        "responsibleRole": "Stakeholder"
                    }
                ]
            },
            {
                "_id": "workflow_development",
                "name": "Desarrollo Iterativo",
                "description": "Proceso de desarrollo incremental",
                "steps": [
                    {
                        "name": "Planificar Iteración",
                        "order": 1,
                        "description": "Definir objetivos de la iteración",
                        "responsibleRole": "Gestor de Proyecto"
                    },
                    {
                        "name": "Diseñar",
                        "order": 2,
                        "description": "Diseñar solución",
                        "responsibleRole": "Arquitecto"
                    },
                    {
                        "name": "Implementar",
                        "order": 3,
                        "description": "Desarrollar funcionalidad",
                        "responsibleRole": "Desarrollador"
                    },
                    {
                        "name": "Probar",
                        "order": 4,
                        "description": "Validar implementación",
                        "responsibleRole": "Probador"
                    },
                    {
                        "name": "Revisar",
                        "order": 5,
                        "description": "Revisar resultados de la iteración",
                        "responsibleRole": "Gestor de Proyecto"
                    }
                ]
            },
            {
                "_id": "workflow_testing",
                "name": "Verificación y Validación",
                "description": "Proceso de pruebas del sistema",
                "steps": [
                    {
                        "name": "Diseñar Casos de Prueba",
                        "order": 1,
                        "description": "Crear casos de prueba",
                        "responsibleRole": "Probador"
                    },
                    {
                        "name": "Ejecutar Pruebas",
                        "order": 2,
                        "description": "Realizar pruebas",
                        "responsibleRole": "Probador"
                    },
                    {
                        "name": "Reportar Defectos",
                        "order": 3,
                        "description": "Documentar problemas encontrados",
                        "responsibleRole": "Probador"
                    },
                    {
                        "name": "Corregir Defectos",
                        "order": 4,
                        "description": "Solucionar problemas",
                        "responsibleRole": "Desarrollador"
                    }
                ]
            }
        ]
    }
    
    # Insert the default configuration
    result = dbConnLocal.clConfigurations.insert_one(default_config)
    print(f"Default configuration created with ID: {result.inserted_id}")
    
    # Create initial history entry
    history_entry = {
        "configurationId": str(result.inserted_id),
        "version": 1,
        "changeDate": datetime.utcnow(),
        "changedBy": "system",
        "changeDescription": "Initial configuration created",
        "previousConfiguration": default_config
    }
    dbConnLocal.clConfigurationHistory.insert_one(history_entry)
    print("Initial history entry created")
    
    print("\n✓ Default OpenUP configuration initialized successfully!")


if __name__ == "__main__":
    initialize_default_configuration()
