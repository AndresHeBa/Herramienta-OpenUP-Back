# HU-025: Gestión de Usuarios y Roles por Proyecto

## Descripción
Sistema completo de gestión de miembros de proyecto con roles específicos (autor, revisor, PO, SM, desarrollador, tester, admin) que permite invitar usuarios, asignar roles, y controlar accesos granulares.

## Características Implementadas

### Backend (Python/Flask)

#### 1. Colección MongoDB: `clProjectMembers`
Estructura de documentos:
```json
{
  "_id": ObjectId,
  "projectId": "string (project _id)",
  "userId": "string (user _id)",
  "roles": ["author", "reviewer", "po", "sm", "developer", "tester", "admin"],
  "status": "pending | active | rejected | removed",
  "invitedBy": "string (user _id)",
  "invitedAt": "datetime",
  "notificationEmail": "string (opcional)",
  "notificationSent": "boolean",
  "acceptedAt": "datetime (opcional)",
  "rejectedAt": "datetime (opcional)",
  "removedAt": "datetime (opcional)",
  "updatedAt": "datetime (opcional)",
  "updatedBy": "string (opcional)",
  "removedBy": "string (opcional)"
}
```

#### 2. Funciones de Backend (`projectMembersFunctions.py`)

**fnInviteMember(project_id, user_id, roles, invited_by, notification_email)**
- Invita un usuario a un proyecto con roles específicos
- Valida que los roles sean válidos
- Verifica que el usuario no esté ya invitado o sea miembro
- Registra auditoría de la invitación

**fnAcceptInvitation(invitation_id, user_id)**
- Acepta una invitación pendiente
- Actualiza el estado a 'active'
- Registra fecha de aceptación y auditoría

**fnRejectInvitation(invitation_id, user_id)**
- Rechaza una invitación pendiente
- Actualiza el estado a 'rejected'
- Registra auditoría del rechazo

**fnGetProjectMembers(project_id, status)**
- Obtiene los miembros de un proyecto
- Permite filtrar por estado (pending, active, rejected, removed)
- Enriquece los datos con información de usuarios (username, email)
- Incluye información del invitador

**fnUpdateMemberRoles(member_id, roles, updated_by)**
- Actualiza los roles de un miembro activo
- Valida que los nuevos roles sean válidos
- Registra auditoría con roles anteriores y nuevos

**fnRemoveMember(member_id, removed_by)**
- Remueve un miembro del proyecto (baja lógica)
- Actualiza el estado a 'removed'
- Registra auditoría de la remoción

**fnGetUserProjects(user_id, status)**
- Obtiene todos los proyectos donde un usuario es miembro
- Incluye los roles del usuario en cada proyecto
- Permite filtrar por estado de membresía

**fnCheckUserProjectAccess(user_id, project_id, required_role)**
- Verifica si un usuario tiene acceso a un proyecto
- Opcionalmente verifica si tiene un rol específico
- Retorna roles, estado de membresía y acceso booleano

**fnGetPendingInvitations(user_id)**
- Obtiene todas las invitaciones pendientes de un usuario
- Enriquece con información del proyecto y del invitador

#### 3. Endpoints REST (`projectMembersDirections.py`)

```
POST   /api/project-members/invite
       Body: { projectId, userId, roles[], invitedBy, notificationEmail? }
       Permiso: manage_team

PUT    /api/project-members/accept/<invitation_id>
       Body: { userId }
       Sin permisos (el usuario acepta su propia invitación)

PUT    /api/project-members/reject/<invitation_id>
       Body: { userId }
       Sin permisos (el usuario rechaza su propia invitación)

GET    /api/project-members/project/<project_id>?status=active,pending
       Permiso: view_team

PUT    /api/project-members/update-roles/<member_id>
       Body: { roles[], updatedBy }
       Permiso: manage_team

DELETE /api/project-members/remove/<member_id>
       Body: { removedBy }
       Permiso: manage_team

GET    /api/project-members/user/<user_id>/projects?status=active
       Sin permisos (lista pública de proyectos del usuario)

POST   /api/project-members/check-access
       Body: { userId, projectId, requiredRole? }
       Sin permisos (verificación de acceso)

GET    /api/project-members/user/<user_id>/invitations
       Sin permisos (usuario consulta sus propias invitaciones)

GET    /api/project-members/roles
       Sin permisos (lista de roles disponibles)
```

### Frontend (Angular)

#### 1. Servicio: `ProjectMembersService`

**Interfaces TypeScript:**
- `ProjectRole`: Información de rol (id, name, description)
- `MemberInvitation`: Estructura de invitación
- `ProjectMember`: Estructura de miembro (extends MemberInvitation)
- `ProjectMembersResponse`, `UserProjectsResponse`, etc.

**Métodos principales:**
- `getAvailableRoles()`: Lista roles disponibles
- `inviteMember(request)`: Envía invitación
- `acceptInvitation(invitationId, userId)`: Acepta invitación
- `rejectInvitation(invitationId, userId)`: Rechaza invitación
- `getProjectMembers(projectId, status?)`: Lista miembros del proyecto
- `updateMemberRoles(memberId, roles, updatedBy)`: Actualiza roles
- `removeMember(memberId, removedBy)`: Remueve miembro
- `getUserProjects(userId, status)`: Proyectos del usuario
- `checkUserProjectAccess(userId, projectId, requiredRole?)`: Verifica acceso
- `getPendingInvitations(userId)`: Invitaciones pendientes

**Helpers:**
- `getRoleLabel(roleId)`: Etiqueta en español del rol
- `getRoleColor(roleId)`: Color asociado al rol
- `getStatusLabel(status)`: Etiqueta en español del estado
- `getStatusColor(status)`: Color asociado al estado

#### 2. Componente: `ProjectMembersComponent`

**Funcionalidades:**
- Lista todos los miembros del proyecto con su información
- Formulario para invitar nuevos miembros con selección múltiple de roles
- Edición inline de roles de miembros existentes
- Remoción de miembros con confirmación
- Filtro por estado (todos, pendientes, activos, rechazados, removidos)
- Badges coloridos para roles y estados
- Formato de fechas amigable
- Manejo de estados de carga y errores

**Diseño:**
- Modal responsive de tamaño completo
- Tabla con información detallada de miembros
- Checkboxes para selección de roles múltiples
- Botones de acción contextual según el estado
- Colores consistentes con el sistema de diseño

#### 3. Integración en `VentanaCreacionComponent`

- Botón "Miembros" en la sección de detalles del proyecto
- Modal que se abre al hacer click
- Variables de estado: `mostrarMembersModal`, `selectedProjectIdForMembers`
- Métodos: `openMembersModal()`, `closeMembersModal()`
- Estilos CSS para botón y modal con gradiente verde

## Roles Disponibles

| ID | Nombre | Descripción | Color |
|----|--------|-------------|-------|
| `author` | Autor | Crea artefactos | Azul |
| `reviewer` | Revisor | Revisa y aprueba artefactos | Púrpura |
| `po` | Product Owner | Gestiona backlog y prioridades | Verde |
| `sm` | Scrum Master | Facilita el proceso | Naranja |
| `developer` | Desarrollador | Implementa funcionalidades | Cyan |
| `tester` | Tester | Realiza pruebas | Rosa |
| `admin` | Admin | Permisos completos en el proyecto | Rojo |

## Permisos Requeridos

Para gestionar miembros de proyecto, se requieren los siguientes permisos:

- `manage_team`: Invitar, actualizar roles, y remover miembros
- `view_team`: Ver la lista de miembros del proyecto

Los usuarios pueden:
- Ver sus propias invitaciones sin permisos especiales
- Aceptar o rechazar sus propias invitaciones sin permisos especiales
- Ver la lista de proyectos donde son miembros sin permisos especiales

## Integración con Auditoría (HU-024)

Todas las operaciones de gestión de miembros se registran en el sistema de auditoría:

- **Invitar miembro**: `action_type='create'`, `entity_type='project'`
- **Aceptar invitación**: `action_type='edit'`, `entity_type='project'`
- **Rechazar invitación**: `action_type='edit'`, `entity_type='project'`
- **Actualizar roles**: `action_type='edit'`, `entity_type='project'`, incluye roles antiguos y nuevos
- **Remover miembro**: `action_type='delete'`, `entity_type='project'`

## Uso

### 1. Invitar un miembro

**Desde la UI:**
1. Abrir detalles de un proyecto
2. Click en botón "Miembros"
3. Click en "+ Invitar Miembro"
4. Ingresar ID de usuario (ejemplo: "2" para autor1)
5. Seleccionar uno o más roles
6. Opcionalmente ingresar email para notificación
7. Click en "Enviar Invitación"

**Desde la API:**
```bash
curl -X POST http://localhost:6002/api/project-members/invite \
  -H "Content-Type: application/json" \
  -H "X-User-Roles: admin" \
  -d '{
    "projectId": "674f8e1234567890abcdef01",
    "userId": "2",
    "roles": ["author", "reviewer"],
    "invitedBy": "1",
    "notificationEmail": "usuario@ejemplo.com"
  }'
```

### 2. Aceptar invitación

```bash
curl -X PUT http://localhost:6002/api/project-members/accept/674f8e1234567890abcdef02 \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "2"
  }'
```

### 3. Ver miembros del proyecto

**Desde la UI:**
1. Abrir detalles de un proyecto
2. Click en botón "Miembros"
3. Usar filtro de estado si es necesario

**Desde la API:**
```bash
# Todos los miembros
curl http://localhost:6002/api/project-members/project/674f8e1234567890abcdef01

# Solo miembros activos
curl http://localhost:6002/api/project-members/project/674f8e1234567890abcdef01?status=active

# Múltiples estados
curl http://localhost:6002/api/project-members/project/674f8e1234567890abcdef01?status=active,pending
```

### 4. Actualizar roles

**Desde la UI:**
1. En la lista de miembros, click en "Editar" junto a un miembro activo
2. Seleccionar/deseleccionar roles
3. Click en "Guardar"

**Desde la API:**
```bash
curl -X PUT http://localhost:6002/api/project-members/update-roles/674f8e1234567890abcdef02 \
  -H "Content-Type: application/json" \
  -H "X-User-Roles: admin" \
  -d '{
    "roles": ["author", "developer", "tester"],
    "updatedBy": "1"
  }'
```

### 5. Remover miembro

**Desde la UI:**
1. En la lista de miembros, click en "Remover"
2. Confirmar la acción

**Desde la API:**
```bash
curl -X DELETE http://localhost:6002/api/project-members/remove/674f8e1234567890abcdef02 \
  -H "Content-Type: application/json" \
  -H "X-User-Roles: admin" \
  -d '{
    "removedBy": "1"
  }'
```

### 6. Verificar acceso de usuario

```bash
curl -X POST http://localhost:6002/api/project-members/check-access \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "2",
    "projectId": "674f8e1234567890abcdef01",
    "requiredRole": "author"
  }'
```

**Respuesta:**
```json
{
  "intCode": 200,
  "strMessage": "success",
  "data": {
    "hasAccess": true,
    "roles": ["author", "reviewer"],
    "status": "active",
    "memberId": "674f8e1234567890abcdef02"
  }
}
```

## Ejemplos de Uso Práctico

### Caso 1: Agregar un desarrollador al proyecto

```typescript
// Frontend
const request: InviteMemberRequest = {
  projectId: 'P-001',
  userId: '5',  // ID del usuario desarrollador
  roles: ['developer'],
  invitedBy: '1',  // Admin actual
  notificationEmail: 'dev@empresa.com'
};

this.membersService.inviteMember(request).subscribe({
  next: (response) => {
    console.log('Desarrollador invitado:', response.data);
  }
});
```

### Caso 2: Usuario acepta invitación

```typescript
// Frontend - Usuario ve sus invitaciones pendientes
this.membersService.getPendingInvitations('5').subscribe({
  next: (response) => {
    const invitations = response.data.invitations;
    // Usuario selecciona una y la acepta
    const invitation = invitations[0];
    
    this.membersService.acceptInvitation(invitation._id, '5').subscribe({
      next: () => {
        console.log('Invitación aceptada, ahora eres miembro del proyecto');
      }
    });
  }
});
```

### Caso 3: Promover miembro de autor a revisor

```typescript
// Frontend - Admin actualiza roles
const memberId = 'member-id-123';
const newRoles = ['author', 'reviewer'];  // Agregar rol de revisor

this.membersService.updateMemberRoles(memberId, newRoles, '1').subscribe({
  next: () => {
    console.log('Roles actualizados correctamente');
  }
});
```

## Estados de Membresía

| Estado | Descripción | Puede cambiar a |
|--------|-------------|-----------------|
| `pending` | Invitación enviada, esperando respuesta | active, rejected |
| `active` | Miembro activo del proyecto | removed |
| `rejected` | Usuario rechazó la invitación | - |
| `removed` | Miembro removido del proyecto | - |

## Notas Importantes

1. **IDs de Usuario**: Actualmente se usa un ID de usuario hardcodeado ("1"). En producción, debe obtenerse del `AuthService`.

2. **Notificaciones por Email**: La funcionalidad de enviar emails está preparada pero no implementada. Se debe integrar con un servicio de email (SendGrid, AWS SES, etc.).

3. **Permisos**: Los permisos `manage_team` y `view_team` deben ser configurados en la matriz de permisos del sistema.

4. **Validación de Usuario**: No se valida si el `userId` existe antes de invitar. Se debe implementar una validación contra `clUsers`.

5. **Roles Personalizados**: Los roles están definidos en `PROJECT_ROLES` en el backend. Para agregar nuevos roles, actualizar esta lista y el servicio Angular.

6. **Integración con Permisos**: El sistema está diseñado para verificar roles de proyecto, pero aún no se integra completamente con el sistema de permisos global. Se recomienda implementar un middleware que verifique roles de proyecto además de roles globales.

## Próximos Pasos

1. **Implementar notificaciones por email** cuando se envía una invitación
2. **Crear componente de invitaciones pendientes** para que usuarios vean y acepten invitaciones desde su dashboard
3. **Integrar verificación de roles de proyecto** en otros componentes (artifacts, iterations, etc.)
4. **Agregar validación de usuario existente** antes de invitar
5. **Implementar paginación** en la lista de miembros para proyectos grandes
6. **Agregar búsqueda y filtros avanzados** en la lista de miembros
7. **Crear reportes de actividad** de miembros del proyecto
8. **Implementar notificaciones en tiempo real** cuando cambian roles o estado de membresía

## Archivos Creados/Modificados

### Backend
- `BackEnd/Functions/projectMembersFunctions.py` (nuevo)
- `BackEnd/Directions/projectMembersDirections.py` (nuevo)
- `Directions.py` (modificado - registrar blueprint)

### Frontend
- `src/app/service/project-members.service.ts` (nuevo)
- `src/app/project-members/project-members.component.ts` (nuevo)
- `src/app/project-members/project-members.component.html` (nuevo)
- `src/app/project-members/project-members.component.css` (nuevo)
- `src/app/ventana-creacion/ventana-creacion.component.ts` (modificado)
- `src/app/ventana-creacion/ventana-creacion.component.html` (modificado)
- `src/app/ventana-creacion/ventana-creacion.component.css` (modificado)
