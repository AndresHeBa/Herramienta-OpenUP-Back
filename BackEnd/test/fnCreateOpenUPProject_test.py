import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from bson.objectid import ObjectId
import pytest
from datetime import datetime
from unittest.mock import MagicMock
import mongomock
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
from BackEnd.Functions.projectFunctions import fnPostProject, fnDeleteProject, fnGetProjectList

# Mock de base de datos
from BackEnd.GlobalInfo.Helpers import dbConnection
dbConnection.clProjects = mongomock.MongoClient().db.collection

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
def clean_database():
    """Limpia la base de datos antes y después de cada test"""
    dbConnection.clProjects.delete_many({})
    yield
    dbConnection.clProjects.delete_many({})


def test_create_project_success(sample_data):
    result = fnPostProject(**sample_data)
    assert result == ResponseMessage.message200

def test_delete_project_not_found():
    """Verifica que retorna 404 cuando el proyecto no existe"""
    # Usar un ObjectId válido pero que no existe en la BD
    fake_id = str(ObjectId())
    
    result = fnDeleteProject(fake_id)
    
    assert result == ResponseMessage.message404

def test_prevent_duplicate_project(sample_data):
    # Insertar proyecto inicial
    fnPostProject(**sample_data)
    # Intentar insertar duplicado
    result = fnPostProject(**sample_data)
    
    assert result == ResponseMessage.message409

