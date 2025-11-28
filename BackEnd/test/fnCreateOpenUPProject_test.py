import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from bson.objectid import ObjectId
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import mongomock
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
from BackEnd.Functions.projectFunctions import (
    fnPostProject, 
    fnDeleteProject, 
    fnGetProjectList, 
    fnGetProject,
    fnDeactivateProject,
    fnUpdateProject
)

# Mock de base de datos
from BackEnd.GlobalInfo.Helpers import dbConnection

@pytest.fixture
def sample_data():
    return {
        "name": "Proyecto Integrador",
        "identifier": "PI-2025",
        "startDate": "2025-02-01",
        "description": "Proyecto académico basado en OpenUP",
        "responsible": "Juan Pérez",
        "tags": ["educación", "flask", "angular"],
        "phases": ["Incepción", "Elaboración", "Construcción", "Transición"]
    }

@pytest.fixture(autouse=True)
def setup_database():
    """Configura y limpia la base de datos antes y después de cada test"""
    # Configurar mock de MongoDB antes de cada test
    dbConnection.clProjects = mongomock.MongoClient().db.collection
    yield
    # Limpiar después de cada test
    dbConnection.clProjects.delete_many({})


# ==================== PRUEBAS EXISTENTES ====================
def test_create_project_success(sample_data):
    result = fnPostProject(**sample_data)
    assert result == ResponseMessage.message200

def test_delete_project_not_found():
    """Verifica que retorna 404 cuando el proyecto no existe"""
    fake_id = str(ObjectId())
    result = fnDeleteProject(fake_id)
    assert result == ResponseMessage.message404

def test_prevent_duplicate_project(sample_data):
    # Insertar proyecto inicial
    fnPostProject(**sample_data)
    # Intentar insertar duplicado
    result = fnPostProject(**sample_data)
    assert result == ResponseMessage.message409


# ==================== NUEVAS PRUEBAS ====================

# --- Pruebas para fnPostProject ---
def test_create_project_duplicate_name_only(sample_data):
    """Verifica que no se permita duplicar solo el nombre"""
    fnPostProject(**sample_data)
    
    # Cambiar identifier pero mantener el mismo name
    sample_data["identifier"] = "PI-2026"
    result = fnPostProject(**sample_data)
    
    assert result == ResponseMessage.message409

def test_create_project_duplicate_identifier_only(sample_data):
    """Verifica que no se permita duplicar solo el identificador"""
    fnPostProject(**sample_data)
    
    # Cambiar name pero mantener el mismo identifier
    sample_data["name"] = "Proyecto Diferente"
    result = fnPostProject(**sample_data)
    
    assert result == ResponseMessage.message409

def test_create_project_with_custom_status(sample_data):
    """Verifica que se pueda crear proyecto con status personalizado"""
    # Usar datos únicos para evitar conflictos
    sample_data["name"] = "Proyecto Custom Status"
    sample_data["identifier"] = "PCS-2025"
    sample_data["status"] = "En Progreso"
    result = fnPostProject(**sample_data)
    
    assert result == ResponseMessage.message200
    
    # Verificar que el status fue guardado correctamente
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    assert project["status"] == "En Progreso"

def test_create_project_phases_format(sample_data):
    """Verifica que las fases se creen con el formato correcto"""
    # Usar datos únicos
    sample_data["name"] = "Proyecto Phases"
    sample_data["identifier"] = "PP-2025"
    fnPostProject(**sample_data)
    
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    
    assert project is not None
    assert len(project["phases"]) == 4
    for phase in project["phases"]:
        assert "name" in phase
        assert "status" in phase
        assert phase["status"] == "Pendiente"

def test_create_project_inactive(sample_data):
    """Verifica que se pueda crear proyecto inactivo"""
    # Usar datos únicos
    sample_data["name"] = "Proyecto Inactive"
    sample_data["identifier"] = "PI-INACT-2025"
    sample_data["active"] = False
    result = fnPostProject(**sample_data)
    
    assert result == ResponseMessage.message200
    
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    assert project["active"] == False


# --- Pruebas para fnGetProjectList ---
def test_get_project_list_empty():
    """Verifica que retorne lista vacía cuando no hay proyectos"""
    result = fnGetProjectList()
    
    assert result["intCode"] == ResponseMessage.message200["intCode"]
    assert result["Result"]["length"] == 0
    assert len(result["Result"]["listResult"]) == 0

def test_get_project_list_multiple_projects(sample_data):
    """Verifica que retorne todos los proyectos"""
    # Crear 3 proyectos con datos únicos
    sample_data["name"] = "Proyecto 1"
    sample_data["identifier"] = "P1-2025"
    fnPostProject(**sample_data)
    
    sample_data["name"] = "Proyecto 2"
    sample_data["identifier"] = "P2-2025"
    fnPostProject(**sample_data)
    
    sample_data["name"] = "Proyecto 3"
    sample_data["identifier"] = "P3-2025"
    fnPostProject(**sample_data)
    
    result = fnGetProjectList()
    
    assert result["intCode"] == ResponseMessage.message200["intCode"]
    assert result["Result"]["length"] == 3
    assert len(result["Result"]["listResult"]) == 3

def test_get_project_list_id_as_string(sample_data):
    """Verifica que los IDs se conviertan a string"""
    fnPostProject(**sample_data)
    
    result = fnGetProjectList()
    
    for project in result["Result"]["listResult"]:
        assert isinstance(project["_id"], str)


# --- Pruebas para fnGetProject ---
def test_get_project_success(sample_data):
    """Verifica que se obtenga un proyecto correctamente"""
    # Usar datos únicos
    sample_data["name"] = "Proyecto Get Success"
    sample_data["identifier"] = "PGS-2025"
    fnPostProject(**sample_data)
    
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    project_id = str(project["_id"])
    
    result = fnGetProject(project_id)
    
    assert result["intCode"] == ResponseMessage.message200["intCode"]
    assert result["Result"]["name"] == sample_data["name"]
    assert result["Result"]["identifier"] == sample_data["identifier"]

def test_get_project_invalid_id():
    """Verifica que retorne 202 con ID inválido"""
    result = fnGetProject("invalid_id_123")
    
    assert result["intCode"] == ResponseMessage.message202["intCode"]
    assert result["data"] == "invalid project id"

def test_get_project_not_found():
    """Verifica que retorne 404 cuando el proyecto no existe"""
    fake_id = str(ObjectId())
    result = fnGetProject(fake_id)
    
    assert result == ResponseMessage.message404


# --- Pruebas para fnDeleteProject ---
def test_delete_project_success(sample_data):
    """Verifica que se elimine un proyecto correctamente"""
    # Usar datos únicos
    sample_data["name"] = "Proyecto Delete Success"
    sample_data["identifier"] = "PDS-2025"
    fnPostProject(**sample_data)
    
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    project_id = str(project["_id"])
    
    result = fnDeleteProject(project_id)
    
    assert result == ResponseMessage.message200
    
    # Verificar que realmente se eliminó
    deleted_project = dbConnection.clProjects.find_one({"_id": ObjectId(project_id)})
    assert deleted_project is None

def test_delete_project_invalid_id():
    """Verifica que retorne 202 con ID inválido"""
    result = fnDeleteProject("invalid_id_123")
    
    assert result["intCode"] == ResponseMessage.message202["intCode"]
    assert result["data"] == "invalid testimonial id"  # Nota: el mensaje dice "testimonial" en el código original


# --- Pruebas para fnDeactivateProject ---
def test_deactivate_project_success(sample_data):
    """Verifica que se desactive un proyecto correctamente"""
    # Usar datos únicos
    sample_data["name"] = "Proyecto Deactivate Success"
    sample_data["identifier"] = "PDEACT-2025"
    fnPostProject(**sample_data)
    
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    project_id = str(project["_id"])
    
    result = fnDeactivateProject(project_id)
    
    assert result == ResponseMessage.message200
    
    # Verificar que esté inactivo
    updated_project = dbConnection.clProjects.find_one({"_id": ObjectId(project_id)})
    assert updated_project["active"] == False
    assert "modificationDate" in updated_project

def test_deactivate_project_invalid_id():
    """Verifica que retorne 202 con ID inválido"""
    result = fnDeactivateProject("invalid_id_123")
    
    assert result["intCode"] == ResponseMessage.message202["intCode"]
    assert result["data"] == "invalid project id"

def test_deactivate_project_not_found():
    """Verifica que retorne 404 cuando el proyecto no existe"""
    fake_id = str(ObjectId())
    result = fnDeactivateProject(fake_id)
    
    assert result == ResponseMessage.message404


# --- Pruebas para fnUpdateProject ---
def test_update_project_success(sample_data):
    """Verifica que se actualice un proyecto correctamente"""
    # Usar datos únicos
    sample_data["name"] = "Proyecto Update Success"
    sample_data["identifier"] = "PUS-2025"
    fnPostProject(**sample_data)
    
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    project_id = str(project["_id"])
    
    result = fnUpdateProject(
        project_id,
        "Título Actualizado",
        "Nuevas características",
        "Descripción actualizada",
        True,
        "http://imagen.com",
        "http://icono.com",
        "Updated Title",
        "New Features",
        "Updated Description"
    )
    
    assert result == ResponseMessage.message200
    
    # Verificar cambios
    updated_project = dbConnection.clProjects.find_one({"_id": ObjectId(project_id)})
    assert updated_project["strTitle"] == "Título Actualizado"
    assert "modificationDate" in updated_project

def test_update_project_invalid_id():
    """Verifica que retorne 202 con ID inválido"""
    result = fnUpdateProject(
        "invalid_id",
        "Título",
        "Features",
        "Descripción",
        True,
        "url",
        "icon",
        "Title",
        "Features",
        "Description"
    )
    
    assert result["intCode"] == ResponseMessage.message202["intCode"]
    assert result["data"] == "invalid project id"

def test_update_project_not_found():
    """Verifica que retorne 404 cuando el proyecto no existe"""
    fake_id = str(ObjectId())
    result = fnUpdateProject(
        fake_id,
        "Título",
        "Features",
        "Descripción",
        True,
        "url",
        "icon",
        "Title",
        "Features",
        "Description"
    )
    
    assert result == ResponseMessage.message404


# --- Pruebas de integración ---
def test_full_project_lifecycle(sample_data):
    """Prueba el ciclo completo: crear, obtener, actualizar, desactivar, eliminar"""
    # Usar datos únicos
    sample_data["name"] = "Proyecto Lifecycle"
    sample_data["identifier"] = "PLC-2025"
    
    # Crear
    result = fnPostProject(**sample_data)
    assert result == ResponseMessage.message200
    
    # Obtener ID
    project = dbConnection.clProjects.find_one({"identifier": sample_data["identifier"]})
    project_id = str(project["_id"])
    
    # Obtener
    result = fnGetProject(project_id)
    assert result["intCode"] == ResponseMessage.message200["intCode"]
    
    # Actualizar
    result = fnUpdateProject(
        project_id, "Nuevo", "F", "D", True, "u", "i", "New", "F", "D"
    )
    assert result == ResponseMessage.message200
    
    # Desactivar
    result = fnDeactivateProject(project_id)
    assert result == ResponseMessage.message200
    
    # Eliminar
    result = fnDeleteProject(project_id)
    assert result == ResponseMessage.message200
    
    # Verificar eliminación
    result = fnGetProject(project_id)
    assert result == ResponseMessage.message404