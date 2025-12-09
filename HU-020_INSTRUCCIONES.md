# HU-020: Reasignar entregables a etapas o flujos

## Descripción
Esta historia de usuario permite mover artefactos entre diferentes fases del proyecto OpenUP, preservando todo el historial de versiones y estados. Incluye validación de reglas de negocio y registro de movimientos.

## Implementación Completada

### Backend

#### 1. Nuevas Funciones en `artifactFunctions.py`

- **`fnReassignArtifactPhase(artifact_id, new_phase, user_id, reason=None)`**
  - Reasigna un artefacto a una nueva fase
  - Valida reglas de negocio antes de mover
  - Registra el movimiento en `clArtifactMovements`
  - Preserva historial de versiones y estados
  - Retorna advertencias si hay violaciones de reglas

- **`_validate_phase_reassignment(project_id, old_phase, new_phase, artifact_type)`**
  - Valida si el movimiento es permitido
  - Verifica artefactos obligatorios para fase Transición
  - Detecta movimientos hacia atrás en el flujo
  - Retorna advertencias sin bloquear (excepto artefactos obligatorios faltantes)

- **`_check_mandatory_artifacts_completion(project_id)`**
  - Verifica que todos los artefactos obligatorios estén subidos
  - Usado para validar entrada a fase Transición

- **`fnGetArtifactMovementHistory(artifact_id)`**
  - Obtiene el historial completo de movimientos de un artefacto
  - Retorna lista ordenada por fecha descendente

#### 2. Nuevos Endpoints en `artifactDirections.py`

- **`PUT /api/artifacts/reassignPhase/<artifactId>`**
  - Requiere permiso: `reassign_artifact`
  - Body: `{ newPhase, userId, reason, force? }`
  - Response: `{ status, message, data: { artifactId, oldPhase, newPhase, movedAt } }`

- **`GET /api/artifacts/movementHistory/<artifactId>`**
  - No requiere autenticación especial
  - Response: `{ status, data: [{ oldPhase, newPhase, movedBy, movedAt, reason, version }] }`

#### 3. Nueva Colección MongoDB: `clArtifactMovements`

Estructura del documento:
```json
{
  "_id": ObjectId,
  "artifactId": "string",
  "projectId": "string",
  "artifactType": "string",
  "oldPhase": "string",
  "newPhase": "string",
  "movedBy": "string",
  "movedAt": ISODate,
  "reason": "string",
  "version": number
}
```

### Frontend

#### 1. Servicio: `artifact.service.ts`

Nuevos métodos:
- `reassignArtifactPhase(artifactId, newPhase, userId, reason?)`
- `getArtifactMovementHistory(artifactId)`

#### 2. Componente: `artifact-uploader.component.ts`

Nuevas propiedades:
```typescript
reassignModalIndex: number | null
reassignTargetPhase: Phase | null
reassignReason: string
movementHistory: any[]
showMovementHistory: boolean
isReassigning: boolean
```

Nuevos métodos:
- `openReassignModal(index)` - Abre modal de reasignación
- `closeReassignModal()` - Cierra modal
- `toggleMovementHistory()` - Muestra/oculta historial
- `getAvailablePhases()` - Fases disponibles (excluye fase actual)
- `performReassignment()` - Ejecuta la reasignación con confirmación
- `performReassignmentWithForce()` - Forzar reasignación (permisos admin)
- `getArtifactAtIndex(index)` - Helper para obtener artefacto

#### 3. Template: `artifact-uploader.component.html`

- Nuevo botón "Mover" en columna de acciones
- Modal completo con:
  - Selector de fase destino
  - Campo de razón obligatorio
  - Historial de movimientos previos (desplegable)
  - Advertencias de validación
  - Confirmación antes de ejecutar

#### 4. Estilos: `artifact-uploader.component.css`

- `.btn-reassign` - Botón morado para reasignar
- `.movement-history-section` - Sección de historial
- `.alert-warning` - Advertencias visuales
- `.form-control` - Inputs estilizados

## Configuración de Permisos

### Agregar el permiso `reassign_artifact`

Ejecutar en MongoDB o a través de la API de permisos:

```javascript
// Opción 1: Insertar directamente en MongoDB
db.clPermissions.insertOne({
  action: "reassign_artifact",
  roles: ["admin", "product_owner"],
  createdAt: new Date()
})

// Opción 2: PATCH via API (requiere admin)
// PUT /api/permissions/reassign_artifact
// Body: { "roles": ["admin", "product_owner"] }
```

### Roles Recomendados
- **admin**: Acceso completo sin restricciones
- **product_owner**: Puede reasignar artefactos para corregir errores
- **project_manager**: Opcional, según necesidades del proyecto

## Reglas de Validación

### Criterio 1: Registro de Movimiento ✅
- Cada movimiento se registra en `clArtifactMovements`
- Incluye: usuario, fecha, razón, fases origen/destino
- Historial completo visible en modal

### Criterio 2: Preservación de Historia ✅
- El artefacto en `clArtifacts` solo cambia el campo `phase`
- Todas las versiones (`version`, `filePath`, `observations`) se mantienen
- Estados de workflow se preservan
- Solo se actualiza `lastModifiedBy` y `lastModifiedAt`

### Criterio 3: Validación y Confirmación ✅

**Regla crítica - Bloquea movimiento:**
- ❌ No permitir mover a "Transición" si faltan artefactos obligatorios de fases previas
  - Mensaje: "Cannot move to Transition: Missing mandatory artifacts - [lista]"

**Advertencias - No bloquean pero requieren confirmación:**
- ⚠️ Mover hacia atrás en el flujo (ej: Construcción → Elaboración)
- ⚠️ Artefacto ya tiene múltiples movimientos previos

**Confirmación en Frontend:**
- Diálogo de confirmación muestra:
  - Artefacto, fase origen, fase destino
  - Razón proporcionada
  - Advertencias si existen
- Usuario debe confirmar explícitamente antes de ejecutar

## Casos de Uso

### Caso 1: Artefacto subido en fase incorrecta
**Situación:** Usuario sube "Modelo de Diseño Detallado" en Elaboración por error
**Solución:**
1. En Elaboración, click en "Mover" del artefacto
2. Seleccionar "Construcción"
3. Razón: "Artefacto corresponde a fase de Construcción"
4. Confirmar
5. Artefacto ahora aparece en Construcción con todo su historial

### Caso 2: Reorganización de artefactos durante revisión
**Situación:** Durante revisión se determina que "Prototipo UI" debe estar en Construcción
**Solución:**
1. Desde fase actual, abrir modal de reasignación
2. Ver historial de movimientos previos
3. Seleccionar fase destino
4. Proporcionar justificación para auditoría
5. Sistema valida y mueve si cumple reglas

### Caso 3: Intento de cerrar proyecto sin artefactos obligatorios
**Situación:** Usuario intenta mover artefactos a Transición prematuramente
**Resultado:**
- Sistema detecta artefactos obligatorios faltantes
- Bloquea el movimiento
- Muestra lista de artefactos pendientes
- Usuario debe completar primero los obligatorios

## Testing

### Test Manual

1. **Movimiento básico:**
   ```
   - Subir artefacto en Incepción
   - Mover a Elaboración con razón válida
   - Verificar que aparece en Elaboración
   - Verificar historial de movimientos
   ```

2. **Validación de Transición:**
   ```
   - Intentar mover artefacto a Transición sin completar obligatorios
   - Verificar mensaje de error con lista de faltantes
   - Completar artefactos obligatorios
   - Reintentar movimiento (debe tener éxito)
   ```

3. **Historial de movimientos:**
   ```
   - Mover artefacto múltiples veces
   - Abrir modal y ver historial
   - Verificar que muestra todos los movimientos
   - Verificar orden cronológico (más reciente primero)
   ```

4. **Preservación de versiones:**
   ```
   - Subir artefacto v1 en Incepción
   - Subir v2
   - Mover a Elaboración
   - Abrir "Historial" y verificar que v1 y v2 se preservan
   ```

### Comandos MongoDB para Verificar

```javascript
// Ver movimientos de un artefacto
db.clArtifactMovements.find({ artifactId: "ARTIFACT_ID_AQUI" }).sort({ movedAt: -1 })

// Ver todos los movimientos de un proyecto
db.clArtifactMovements.find({ projectId: "P-001" }).sort({ movedAt: -1 })

// Estadísticas de movimientos
db.clArtifactMovements.aggregate([
  { $group: { _id: "$movedBy", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

## Próximos Pasos (Opcional)

1. **Notificaciones:** Enviar notificación a equipo cuando se mueve artefacto crítico
2. **Auditoría avanzada:** Dashboard con estadísticas de movimientos
3. **Permisos granulares:** Restricciones por fase o tipo de artefacto
4. **Movimiento masivo:** Mover múltiples artefactos a la vez
5. **Reversión:** Deshacer último movimiento (solo admin)

## Notas Técnicas

- Los artefactos mantienen su `_id` al moverse (no se duplican)
- El campo `phase` es el único que cambia en el documento principal
- La colección `clArtifactMovements` es independiente y puede crecer indefinidamente
- Se recomienda crear índice en `clArtifactMovements`:
  ```javascript
  db.clArtifactMovements.createIndex({ artifactId: 1, movedAt: -1 })
  db.clArtifactMovements.createIndex({ projectId: 1 })
  ```

## Soporte

Para dudas o problemas:
1. Revisar logs del backend (búsqueda: "✅ Artifact")
2. Verificar permisos del usuario (header `X-User-Roles`)
3. Verificar colección `clArtifactMovements` en MongoDB
4. Revisar console del navegador para errores frontend
