"""
Script de inicialización para HU-020: Reasignar entregables a etapas o flujos

Este script:
1. Crea la colección clArtifactMovements si no existe
2. Crea índices para optimizar consultas
3. Agrega el permiso 'reassign_artifact' a la colección de permisos

Ejecutar una sola vez después de implementar HU-020.
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import BackEnd.GlobalInfo.Helpers as HelperFunctions

# Conectar a la base de datos
dbConnLocal = HelperFunctions.dbConnection()

def create_artifact_movements_collection():
    """Crear colección clArtifactMovements si no existe"""
    try:
        # Verificar si la colección existe
        collections = dbConnLocal.list_collection_names()
        
        if 'clArtifactMovements' not in collections:
            dbConnLocal.create_collection('clArtifactMovements')
            print("✅ Colección 'clArtifactMovements' creada exitosamente")
        else:
            print("ℹ️  Colección 'clArtifactMovements' ya existe")
        
        return True
    except Exception as e:
        print(f"❌ Error creando colección: {e}")
        return False


def create_indexes():
    """Crear índices para optimizar consultas"""
    try:
        # Índice compuesto: artifactId + movedAt (descendente)
        # Para consultas de historial de un artefacto específico
        dbConnLocal.clArtifactMovements.create_index(
            [("artifactId", 1), ("movedAt", -1)],
            name="idx_artifact_movements"
        )
        print("✅ Índice 'idx_artifact_movements' creado (artifactId + movedAt)")
        
        # Índice simple: projectId
        # Para consultas de todos los movimientos de un proyecto
        dbConnLocal.clArtifactMovements.create_index(
            [("projectId", 1)],
            name="idx_project_movements"
        )
        print("✅ Índice 'idx_project_movements' creado (projectId)")
        
        # Índice simple: movedAt
        # Para consultas de movimientos recientes o estadísticas temporales
        dbConnLocal.clArtifactMovements.create_index(
            [("movedAt", -1)],
            name="idx_movement_date"
        )
        print("✅ Índice 'idx_movement_date' creado (movedAt)")
        
        return True
    except Exception as e:
        print(f"❌ Error creando índices: {e}")
        return False


def add_reassign_permission():
    """Agregar permiso 'reassign_artifact' a la colección de permisos"""
    try:
        # Verificar si el permiso ya existe
        existing = dbConnLocal.clPermissions.find_one({"action": "reassign_artifact"})
        
        if existing:
            print("ℹ️  Permiso 'reassign_artifact' ya existe")
            print(f"   Roles actuales: {existing.get('roles', [])}")
            return True
        
        # Crear el permiso con roles admin y product_owner
        permission_doc = {
            "action": "reassign_artifact",
            "roles": ["admin", "product_owner"],
            "createdAt": datetime.now(),
            "description": "Permite reasignar artefactos entre fases del proyecto OpenUP"
        }
        
        dbConnLocal.clPermissions.insert_one(permission_doc)
        print("✅ Permiso 'reassign_artifact' creado exitosamente")
        print(f"   Roles autorizados: {permission_doc['roles']}")
        
        return True
    except Exception as e:
        print(f"❌ Error agregando permiso: {e}")
        return False


def verify_setup():
    """Verificar que todo está configurado correctamente"""
    print("\n" + "="*50)
    print("VERIFICACIÓN DE CONFIGURACIÓN")
    print("="*50)
    
    # 1. Verificar colección
    collections = dbConnLocal.list_collection_names()
    if 'clArtifactMovements' in collections:
        print("✅ Colección 'clArtifactMovements' existe")
        count = dbConnLocal.clArtifactMovements.count_documents({})
        print(f"   Documentos actuales: {count}")
    else:
        print("❌ Colección 'clArtifactMovements' NO existe")
    
    # 2. Verificar índices
    indexes = list(dbConnLocal.clArtifactMovements.list_indexes())
    print(f"\n✅ Índices en 'clArtifactMovements': {len(indexes)}")
    for idx in indexes:
        print(f"   - {idx['name']}: {idx.get('key', {})}")
    
    # 3. Verificar permiso
    permission = dbConnLocal.clPermissions.find_one({"action": "reassign_artifact"})
    if permission:
        print(f"\n✅ Permiso 'reassign_artifact' configurado")
        print(f"   Roles: {permission.get('roles', [])}")
    else:
        print("\n❌ Permiso 'reassign_artifact' NO encontrado")
    
    print("\n" + "="*50)


def main():
    """Ejecutar script de inicialización"""
    print("\n" + "="*50)
    print("INICIALIZACIÓN HU-020: REASIGNAR ARTEFACTOS")
    print("="*50 + "\n")
    
    success = True
    
    # Paso 1: Crear colección
    print("Paso 1: Creando colección 'clArtifactMovements'...")
    if not create_artifact_movements_collection():
        success = False
    
    # Paso 2: Crear índices
    print("\nPaso 2: Creando índices...")
    if not create_indexes():
        success = False
    
    # Paso 3: Agregar permiso
    print("\nPaso 3: Agregando permiso 'reassign_artifact'...")
    if not add_reassign_permission():
        success = False
    
    # Verificación final
    verify_setup()
    
    if success:
        print("\n✅ Inicialización completada exitosamente")
        print("\nPróximos pasos:")
        print("1. Reiniciar el servidor backend")
        print("2. Probar funcionalidad desde el frontend")
        print("3. Revisar logs para verificar operación correcta")
    else:
        print("\n⚠️  Inicialización completada con advertencias")
        print("   Revisar mensajes de error arriba")
    
    return success


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        HelperFunctions.PrintException()
        sys.exit(1)
