# HU-024: Auditoría y Registro de Cambios (Trail)

## Descripción
Sistema completo de auditoría que registra todas las acciones críticas en el sistema OpenUP, proporcionando trazabilidad completa y responsabilidad.

## Prioridad: Alta | Estimación: 5 puntos

---

## Criterios de Aceptación

✅ **Todas las acciones críticas quedan registradas** con usuario, fecha y detalle:
- Crear/editar/eliminar artefactos
- Cambios de estado de artefactos
- Creación de nuevas versiones
- Mover artefactos entre fases
- Crear/editar/eliminar proyectos
- Archivar/restaurar proyectos

✅ **El historial es consultable y exportable**:
- Filtrado por proyecto, usuario, tipo de acción, tipo de entidad, rango de fechas
- Paginación de resultados
- Exportación a JSON y CSV
- Estadísticas de auditoría

✅ **Los registros no se pierden al archivar proyectos**:
- Logs persistentes en colección `clAuditLog` de MongoDB
- Referencia a projectId se mantiene incluso si el proyecto es eliminado

---

## Implementación

### Backend (Python/Flask)

#### 1. Modelo de Datos - Colección `clAuditLog`

```python
{
    "_id": ObjectId,
    "userId": str,              # Usuario que realizó la acción
    "actionType": str,          # Tipo de acción (create, edit, delete, status_change, etc.)
    "entityType": str,          # Tipo de entidad (project, artifact, iteration, etc.)
    "entityId": str,            # ID de la entidad afectada
    "projectId": str,           # ID del proyecto relacionado (opcional)
    "timestamp": datetime,       # Fecha y hora de la acción
    "details": dict,            # Detalles adicionales específicos de la acción
    "ipAddress": str,           # IP del usuario (opcional)
    "userAgent": str            # User agent del navegador (opcional)
}
```

#### 2. Funciones Principales (`auditFunctions.py`)

- **`fnLogAuditAction()`**: Registra una acción de auditoría
- **`fnGetAuditLogs()`**: Obtiene logs con filtros y paginación
- **`fnGetProjectAuditHistory()`**: Historial de un proyecto específico
- **`fnGetEntityAuditHistory()`**: Historial de una entidad específica
- **`fnGetUserAuditHistory()`**: Historial de acciones de un usuario
- **`fnExportAuditLogs()`**: Exporta logs en JSON o CSV
- **`fnGetAuditStats()`**: Obtiene estadísticas de auditoría

#### 3. Endpoints REST (`auditDirections.py`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/audit/logs` | Obtiene logs con filtros opcionales |
| GET | `/api/audit/project/<projectId>` | Historial de un proyecto |
| GET | `/api/audit/entity/<entityType>/<entityId>` | Historial de una entidad |
| GET | `/api/audit/user/<userId>` | Historial de un usuario |
| GET | `/api/audit/export` | Exporta logs (JSON/CSV) |
| GET | `/api/audit/stats` | Estadísticas de auditoría |
| POST | `/api/audit/log` | Crea registro manual (admin) |

#### 4. Helper para Logging (`Helpers.py`)

```python
def logAudit(user_id, action_type, entity_type, entity_id, details=None, project_id=None):
    """
    Helper function para registrar acciones de auditoría desde cualquier función
    """
```

#### 5. Integración en Operaciones Existentes

**Artefactos (`artifactFunctions.py`):**
- ✅ `fnUploadArtifact()` - Registra creación de artefactos
- ✅ `fnUpdateArtifactState()` - Registra cambios de estado
- ✅ `fnReassignArtifactPhase()` - Registra movimientos entre fases

**Proyectos (`projectFunctions.py`):**
- ✅ `fnPostProject()` - Registra creación de proyectos
- ✅ `fnUpdateOpenUPProject()` - Registra ediciones
- ✅ `fnDeleteProject()` - Registra eliminaciones

### Frontend (Angular)

#### 1. Servicio de Auditoría (`audit.service.ts`)

**Interfaces TypeScript:**
```typescript
interface AuditLog {
  _id: string;
  userId: string;
  actionType: 'create' | 'edit' | 'delete' | 'status_change' | 'version_create' | 'move' | 'archive' | 'restore' | 'export' | 'import';
  entityType: 'project' | 'artifact' | 'iteration' | 'microincrement' | 'build' | 'workflow' | 'configuration' | 'plan';
  entityId?: string;
  projectId?: string;
  timestamp: string;
  details: any;
}

interface AuditFilters {
  projectId?: string;
  userId?: string;
  actionType?: string | string[];
  entityType?: string | string[];
  entityId?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  skip?: number;
}
```

**Métodos Principales:**
- `getAuditLogs(filters?)`: Obtiene logs con filtros
- `getProjectAuditHistory(projectId)`: Historial de proyecto
- `getEntityAuditHistory(entityType, entityId)`: Historial de entidad
- `getUserAuditHistory(userId)`: Historial de usuario
- `getAuditStats()`: Estadísticas
- `exportAuditLogsJSON(filters?)`: Exporta a JSON
- `exportAuditLogsCSV(filters?)`: Exporta a CSV
- `getActionTypeLabel(action)`: Traduce tipo de acción
- `getEntityTypeLabel(entity)`: Traduce tipo de entidad
- `getActionTypeColor(action)`: Color para badge

#### 2. Componente de Visualización (`audit-viewer`)

**Características:**
- 📊 Tabla interactiva de logs con paginación
- 🔍 Filtros por proyecto, usuario, tipo de acción, tipo de entidad, fechas
- 📈 Panel de estadísticas con gráficos
- 📥 Exportación a JSON y CSV
- 🎨 Badges de colores por tipo de acción
- 📱 Diseño responsive

**Uso:**
```html
<!-- Para un proyecto específico -->
<app-audit-viewer [projectId]="projectId"></app-audit-viewer>

<!-- Para una entidad específica -->
<app-audit-viewer 
  [entityType]="'artifact'" 
  [entityId]="artifactId">
</app-audit-viewer>

<!-- Vista general -->
<app-audit-viewer></app-audit-viewer>
```

---

## Tipos de Acciones Registradas

| Acción | Descripción | Color |
|--------|-------------|-------|
| `create` | Creación de entidad | 🟢 Verde |
| `edit` | Edición de entidad | 🔵 Azul |
| `delete` | Eliminación de entidad | 🔴 Rojo |
| `status_change` | Cambio de estado | 🟠 Naranja |
| `version_create` | Nueva versión | 🟣 Morado |
| `move` | Movimiento entre fases | 🔷 Cian |
| `archive` | Archivar entidad | 🟤 Marrón |
| `restore` | Restaurar entidad | 🟡 Verde Lima |
| `export` | Exportación | ⚫ Gris |
| `import` | Importación | 🔷 Azul Oscuro |

---

## Tipos de Entidades Auditadas

- **project**: Proyectos OpenUP
- **artifact**: Artefactos y sus versiones
- **iteration**: Iteraciones
- **microincrement**: Microincrementos
- **build**: Builds/compilaciones
- **workflow**: Flujos de trabajo
- **configuration**: Configuraciones OpenUP
- **plan**: Planes de proyecto

---

## Permisos Requeridos

- **`view_audit`**: Ver logs de auditoría
- **`export_audit`**: Exportar logs de auditoría
- **`create`**: Crear registros manuales (solo admin)

---

## Consultas y Filtros Disponibles

### Por Proyecto
```typescript
auditService.getProjectAuditHistory(projectId, limit, skip);
```

### Por Entidad
```typescript
auditService.getEntityAuditHistory('artifact', artifactId, limit, skip);
```

### Por Usuario
```typescript
auditService.getUserAuditHistory(userId, limit, skip, startDate, endDate);
```

### Con Filtros Complejos
```typescript
const filters: AuditFilters = {
  projectId: 'P-001',
  actionType: ['create', 'edit'],
  entityType: 'artifact',
  startDate: '2025-01-01T00:00:00',
  endDate: '2025-12-31T23:59:59',
  limit: 100,
  skip: 0
};

auditService.getAuditLogs(filters);
```

---

## Estadísticas Disponibles

```typescript
auditService.getAuditStats(projectId?, startDate?, endDate?);

// Retorna:
{
  totalActions: number,
  actionTypeStats: [{ _id: string, count: number }],
  entityTypeStats: [{ _id: string, count: number }],
  topUsers: [{ _id: string, count: number }]
}
```

---

## Exportación de Logs

### JSON
```typescript
auditService.exportAuditLogsJSON(filters).subscribe(response => {
  auditService.downloadJSON(
    response.Result.data,
    'audit_logs_2025.json'
  );
});
```

### CSV
```typescript
auditService.exportAuditLogsCSV(filters).subscribe(blob => {
  auditService.downloadBlob(blob, 'audit_logs_2025.csv');
});
```

---

## Ejemplos de Uso

### 1. Ver Historial de un Proyecto en Detalles

```html
<!-- En ventana-creacion.component.html -->
<div class="detalle-section" *ngIf="mostrarDetalle && detalleProyecto">
  <h3>Historial de Auditoría</h3>
  <app-audit-viewer [projectId]="detalleProyecto._id"></app-audit-viewer>
</div>
```

### 2. Ver Cambios de un Artefacto Específico

```html
<!-- En artifact-uploader.component.html -->
<button (click)="verHistorialArtefacto(artifact._id)">
  Ver Historial
</button>

<!-- Modal -->
<div *ngIf="mostrarHistorialModal">
  <app-audit-viewer 
    [entityType]="'artifact'" 
    [entityId]="selectedArtifactId">
  </app-audit-viewer>
</div>
```

### 3. Dashboard de Auditoría General

```html
<!-- Nueva página de administración -->
<app-audit-viewer></app-audit-viewer>
```

---

## Archivos Creados/Modificados

### Backend
- ✅ `BackEnd/Functions/auditFunctions.py` - Funciones de auditoría
- ✅ `BackEnd/Directions/auditDirections.py` - Endpoints REST
- ✅ `BackEnd/GlobalInfo/Helpers.py` - Helper `logAudit()`
- ✅ `Directions.py` - Registrado blueprint de auditoría
- ✅ `BackEnd/Functions/artifactFunctions.py` - Integrado logging
- ✅ `BackEnd/Functions/projectFunctions.py` - Integrado logging

### Frontend
- ✅ `src/app/service/audit.service.ts` - Servicio Angular
- ✅ `src/app/audit-viewer/audit-viewer.component.ts` - Componente
- ✅ `src/app/audit-viewer/audit-viewer.component.html` - Template
- ✅ `src/app/audit-viewer/audit-viewer.component.css` - Estilos

---

## Testing

### Pruebas Manuales
1. Crear un proyecto → Verificar log en `/api/audit/logs`
2. Subir un artefacto → Verificar log con detalles
3. Cambiar estado de artefacto → Verificar log con `status_change`
4. Mover artefacto de fase → Verificar log con `move`
5. Eliminar proyecto → Verificar log persiste
6. Exportar a JSON y CSV → Verificar formato correcto

### Casos de Prueba
- ✅ Logs se crean correctamente en todas las operaciones
- ✅ Filtros funcionan correctamente
- ✅ Paginación funciona
- ✅ Exportación genera archivos válidos
- ✅ Estadísticas son precisas
- ✅ Logs persisten después de eliminar entidades

---

## Mejoras Futuras

1. **Retención de Logs**: Política de retención automática (ej: mantener 1 año)
2. **Búsqueda Avanzada**: Full-text search en detalles
3. **Alertas**: Notificaciones para acciones críticas
4. **Dashboard**: Visualizaciones gráficas de tendencias
5. **Comparación de Versiones**: Ver diff entre cambios
6. **Logs de Sistema**: Incluir eventos del sistema (backups, errores)
7. **Firma Digital**: Verificación de integridad de logs
8. **Compresión**: Comprimir logs antiguos para ahorrar espacio

---

## Soporte

Para preguntas o problemas con el sistema de auditoría, contactar al equipo de desarrollo.

**Fecha de Implementación**: Diciembre 2025  
**Versión**: 1.0  
**Estado**: ✅ Completado
