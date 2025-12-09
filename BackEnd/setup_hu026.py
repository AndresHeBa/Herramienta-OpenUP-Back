"""
Setup script para HU-026: Project Closure
Agrega los permisos necesarios para cierre de proyectos
"""

from pymongo import MongoClient
from datetime import datetime

def setup_closure_permissions():
    """
    Agrega permisos de cierre de proyecto al sistema
    """
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['myDatabase']
        
        print("=" * 60)
        print("HU-026: Setup de Permisos de Cierre de Proyecto")
        print("=" * 60)
        print()
        
        # Buscar configuración activa
        active_config = db.clOpenUpConfigurations.find_one({'active': True})
        
        if not active_config:
            print("⚠️  No se encontró configuración activa.")
            print("   Buscando en clPermissions legacy...")
            
            # Fallback a colección legacy
            permissions_to_add = [
                {
                    'action': 'close_project',
                    'description': 'Cerrar proyecto generando documento de cierre',
                    'roles': ['admin', 'po', 'sm']
                },
                {
                    'action': 'view_project',
                    'description': 'Ver proyectos y sus detalles',
                    'roles': ['admin', 'po', 'sm', 'author', 'reviewer', 'developer', 'tester']
                },
                {
                    'action': 'reopen_project',
                    'description': 'Reabrir un proyecto cerrado',
                    'roles': ['admin']
                }
            ]
            
            for perm in permissions_to_add:
                existing = db.clPermissions.find_one({'action': perm['action']})
                if existing:
                    print(f"✓ Permiso '{perm['action']}' ya existe")
                else:
                    db.clPermissions.insert_one(perm)
                    print(f"✓ Permiso '{perm['action']}' agregado")
        
        else:
            print(f"✓ Configuración activa encontrada: {active_config['name']}")
            print()
            
            # Verificar y agregar permisos a la configuración activa
            permissions = active_config.get('permissions', [])
            
            permissions_to_check = [
                {
                    'action': 'close_project',
                    'description': 'Cerrar proyecto generando documento de cierre',
                    'roles': ['admin', 'po', 'sm']
                },
                {
                    'action': 'view_project',
                    'description': 'Ver proyectos y sus detalles',
                    'roles': ['admin', 'po', 'sm', 'author', 'reviewer', 'developer', 'tester']
                },
                {
                    'action': 'reopen_project',
                    'description': 'Reabrir un proyecto cerrado',
                    'roles': ['admin']
                }
            ]
            
            modified = False
            
            for perm_check in permissions_to_check:
                # Buscar si ya existe
                exists = any(p.get('action') == perm_check['action'] for p in permissions)
                
                if exists:
                    print(f"✓ Permiso '{perm_check['action']}' ya existe en configuración")
                else:
                    permissions.append(perm_check)
                    modified = True
                    print(f"✓ Permiso '{perm_check['action']}' agregado a configuración")
            
            if modified:
                # Actualizar configuración
                db.clOpenUpConfigurations.update_one(
                    {'_id': active_config['_id']},
                    {'$set': {'permissions': permissions}}
                )
                print()
                print("✅ Configuración actualizada con nuevos permisos")
            else:
                print()
                print("ℹ️  Todos los permisos ya estaban presentes")
        
        print()
        print("=" * 60)
        print("Verificación Final")
        print("=" * 60)
        
        # Verificar permisos finales
        if active_config:
            updated_config = db.clOpenUpConfigurations.find_one({'_id': active_config['_id']})
            closure_perms = [p for p in updated_config.get('permissions', []) 
                           if 'close' in p.get('action', '') or 'reopen' in p.get('action', '')]
            
            print(f"\nPermisos de cierre en configuración activa:")
            for perm in closure_perms:
                print(f"  ✓ {perm['action']} -> Roles: {perm['roles']}")
        else:
            closure_perms = list(db.clPermissions.find({
                '$or': [
                    {'action': {'$regex': 'close'}},
                    {'action': {'$regex': 'reopen'}}
                ]
            }))
            
            print(f"\nPermisos de cierre en clPermissions:")
            for perm in closure_perms:
                print(f"  ✓ {perm['action']} -> Roles: {perm['roles']}")
        
        print()
        print("=" * 60)
        print("✅ Setup completado exitosamente")
        print("=" * 60)
        print()
        print("Próximos pasos:")
        print("1. Reinicia el servidor Flask: python Directions.py")
        print("2. Prueba cerrar un proyecto desde la interfaz")
        print("3. Verifica el documento de cierre generado")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el setup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    setup_closure_permissions()
