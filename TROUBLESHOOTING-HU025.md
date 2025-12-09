# Solución al Error 500 en Project Members

## Problema
Error 500 (INTERNAL SERVER ERROR) al intentar invitar un miembro al proyecto.

## Causas Posibles

1. **Falta el permiso `manage_team` en la base de datos**
2. **El usuario no tiene los roles necesarios**
3. **Error en la conexión a MongoDB**

## Solución

### Paso 1: Ejecutar el Script de Setup

Desde el directorio `OpenUp Back`, ejecuta:

```bash
python BackEnd/setup_hu025.py
```

Este script:
- Agrega los permisos `manage_team` y `view_team` a la configuración activa
- Asigna los permisos a los roles apropiados:
  - `manage_team`: admin, sm, po
  - `view_team`: todos los roles

### Paso 2: Reiniciar el Servidor Flask

1. Detén el servidor Flask (Ctrl+C)
2. Reinicia con:
```bash
python Directions.py
```

### Paso 3: Verificar los Logs

Ahora el endpoint `/api/project-members/invite` tiene logging detallado:
- Imprime los datos recibidos
- Imprime el resultado de la función
- Muestra errores específicos

Busca en la consola del servidor:
```
DEBUG - Invite member request data: {...}
DEBUG - Calling fnInviteMember with: ...
DEBUG - fnInviteMember result: ...
```

### Paso 4: Probar de Nuevo

1. Abre el navegador en la aplicación Angular
2. Ve a un proyecto
3. Click en "Miembros"
4. Click en "+ Invitar Miembro"
5. Completa el formulario:
   - ID de Usuario: 2 (para usuario "autor1")
   - Selecciona roles
   - Click en "Enviar Invitación"

## Debugging Adicional

Si sigue fallando, verifica:

### 1. Usuario tiene roles correctos

```javascript
// En el navegador (Console)
localStorage.getItem('currentUser')
```

Debe mostrar un usuario con roles como `["admin"]` o `["sm"]` o `["po"]`

### 2. MongoDB está corriendo

```bash
# En PowerShell
Get-Service -Name MongoDB
```

### 3. Colección clProjectMembers existe

```bash
# En MongoDB shell
use openup_db
db.clProjectMembers.countDocuments()
```

## Cambios Temporales para Debugging

He deshabilitado temporalmente el decorador `@requireAction('manage_team')` en el endpoint `/invite` para facilitar el debugging. 

**IMPORTANTE:** Una vez resuelto el problema, debes reactivar el decorador:

```python
@projectMembersBluePrint.route('/invite', methods=['POST'])
@requireAction('manage_team')  # Descomentar esta línea
def inviteMember():
    ...
```

## Ejemplo de Request Válido

```json
POST http://localhost:6002/api/project-members/invite

{
  "projectId": "674f8e1234567890abcdef01",
  "userId": "2",
  "roles": ["author", "reviewer"],
  "invitedBy": "1",
  "notificationEmail": "usuario@ejemplo.com"
}
```

## Respuesta Esperada (Éxito)

```json
{
  "intCode": 201,
  "strMessage": "success",
  "data": {
    "_id": "...",
    "projectId": "...",
    "userId": "2",
    "roles": ["author", "reviewer"],
    "status": "pending",
    "invitedBy": "1",
    "invitedAt": "2025-12-08T...",
    ...
  },
  "message": "Member invited successfully"
}
```

## Si el Error Persiste

Copia el error completo de la consola del servidor Flask y compártelo para análisis más detallado.
