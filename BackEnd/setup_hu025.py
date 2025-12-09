"""
Script para agregar permisos necesarios para HU-025: Gestión de Usuarios y Roles por Proyecto

Agrega los permisos:
- manage_team: Gestionar miembros del equipo (invitar, actualizar roles, remover)
- view_team: Ver lista de miembros del equipo
"""

import sys
sys.path.insert(0, '.')

import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = HelperFunctions.dbConnection()

def setup_permissions():
    """Agrega los permisos necesarios para gestión de miembros de proyecto"""
    
    print("=" * 60)
    print("HU-025: Setup - Permisos de Gestión de Miembros")
    print("=" * 60)
    
    # Permisos a agregar
    permissions_to_add = [
        {
            "action": "manage_team",
            "roles": ["admin", "sm", "po"],  # Admin, Scrum Master y Product Owner pueden gestionar el equipo
            "description": "Gestionar miembros del equipo (invitar, actualizar roles, remover)"
        },
        {
            "action": "view_team",
            "roles": ["admin", "sm", "po", "author", "revisor", "developer", "tester"],  # Todos los roles pueden ver el equipo
            "description": "Ver lista de miembros del equipo del proyecto"
        }
    ]
    
    print("\n1. Verificando permisos existentes...")
    
    # Verificar si hay una configuración activa
    active_config = dbConnLocal.clConfigurations.find_one({"active": True})
    
    if active_config:
        print(f"   ✓ Configuración activa encontrada: {active_config.get('name')}")
        
        # Agregar permisos a la configuración activa
        existing_permissions = active_config.get('permissions', [])
        existing_actions = [p.get('action') for p in existing_permissions]
        
        permissions_added = 0
        for perm in permissions_to_add:
            if perm['action'] not in existing_actions:
                existing_permissions.append({
                    'action': perm['action'],
                    'roles': perm['roles'],
                    'description': perm.get('description', '')
                })
                permissions_added += 1
                print(f"   + Agregando permiso: {perm['action']}")
            else:
                print(f"   - Permiso ya existe: {perm['action']}")
        
        if permissions_added > 0:
            # Actualizar configuración
            result = dbConnLocal.clConfigurations.update_one(
                {"_id": active_config['_id']},
                {"$set": {"permissions": existing_permissions}}
            )
            print(f"\n   ✓ {permissions_added} permiso(s) agregado(s) a la configuración activa")
        else:
            print(f"\n   ✓ Todos los permisos ya existen en la configuración activa")
    
    else:
        print("   ! No hay configuración activa")
        print("   Agregando permisos a colección clPermissions (legacy)...")
        
        # Fallback: agregar a clPermissions directamente
        for perm in permissions_to_add:
            existing = dbConnLocal.clPermissions.find_one({"action": perm['action']})
            
            if not existing:
                dbConnLocal.clPermissions.insert_one({
                    "action": perm['action'],
                    "roles": perm['roles']
                })
                print(f"   + Permiso agregado: {perm['action']}")
            else:
                # Actualizar roles si es necesario
                dbConnLocal.clPermissions.update_one(
                    {"action": perm['action']},
                    {"$set": {"roles": perm['roles']}}
                )
                print(f"   - Permiso actualizado: {perm['action']}")
    
    print("\n2. Verificación final...")
    
    # Verificar permisos agregados
    if active_config:
        updated_config = dbConnLocal.clConfigurations.find_one({"active": True})
        permissions = updated_config.get('permissions', [])
    else:
        permissions = list(dbConnLocal.clPermissions.find())
    
    manage_team = next((p for p in permissions if p.get('action') == 'manage_team'), None)
    view_team = next((p for p in permissions if p.get('action') == 'view_team'), None)
    
    if manage_team:
        print(f"   ✓ manage_team -> Roles: {manage_team.get('roles')}")
    else:
        print(f"   ✗ manage_team NO encontrado")
    
    if view_team:
        print(f"   ✓ view_team -> Roles: {view_team.get('roles')}")
    else:
        print(f"   ✗ view_team NO encontrado")
    
    print("\n" + "=" * 60)
    print("Setup completado")
    print("=" * 60)
    print("\nAhora puedes:")
    print("1. Reiniciar el servidor Flask")
    print("2. Usar la funcionalidad de gestión de miembros")
    print("3. Los usuarios con roles 'admin', 'sm', o 'po' pueden gestionar equipos")
    print("4. Todos los usuarios pueden ver la lista de miembros")
    print()

if __name__ == "__main__":
    try:
        setup_permissions()
    except Exception as e:
        print(f"\n✗ Error durante el setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
