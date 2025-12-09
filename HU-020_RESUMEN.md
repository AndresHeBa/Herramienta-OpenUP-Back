# HU-020: Reasignar Entregables a Etapas o Flujos - Resumen de Implementación

## ✅ Estado: IMPLEMENTADO

### Objetivo
Permitir mover artefactos entre diferentes fases del proyecto OpenUP cuando se han subido en la fase incorrecta, preservando todo el historial de versiones y estados del workflow.

---

## Cambios Implementados

### Backend (Python/Flask)

#### Archivos Modificados

1. **`BackEnd/Functions/artifactFunctions.py`**
   - ✅ Agregada función `fnReassignArtifactPhase()` para reasignar artefactos
   - ✅ Agregada función `_validate_phase_reassignment()` para validar reglas de negocio
   - ✅ Agregada función `_check_mandatory_artifacts_completion()` para verificar artefactos obligatorios
   - ✅ Agregada función `fnGetArtifactMovementHistory()` para obtener historial de movimientos

2. **`BackEnd/Directions/artifactDirections.py`**
   - ✅ Agregado endpoint `PUT /api/artifacts/reassignPhase/<artifactId>`
   - ✅ Agregado endpoint `GET /api/artifacts/movementHistory/<artifactId>`
   - ✅ Decorador `@requireAction('reassign_artifact')` para control de permisos

#### Nuevas Colecciones MongoDB

3. **`clArtifactMovements`** (nueva colección)
   ```javascript
   {
     artifactId: string,
     projectId: string,
     artifactType: string,
     oldPhase: string,
     newPhase: string,
     movedBy: string,
     movedAt: ISODate,
     reason: string,
     version: number
   }
   ```

4. **`clPermissions`** (actualizada)
   - ✅ Nuevo permiso `reassign_artifact` agregado
   - Roles autorizados: `admin`, `product_owner`

---

### Frontend (Angular 17+)

#### Archivos Modificados

1. **`src/app/service/artifact.service.ts`**
   - ✅ Método `reassignArtifactPhase()` para llamar al endpoint de reasignación
   - ✅ Método `getArtifactMovementHistory()` para obtener historial

2. **`src/app/artifact-uploader/artifact-uploader.component.ts`**
   - ✅ Propiedades para modal de reasignación
   - ✅ Método `openReassignModal()` para abrir modal
   - ✅ Método `performReassignment()` para ejecutar reasignación
   - ✅ Método `getAvailablePhases()` para listar fases disponibles
   - ✅ Método `toggleMovementHistory()` para mostrar/ocultar historial

3. **`src/app/artifact-uploader/artifact-uploader.component.html`**
   - ✅ Botón "Mover" en cada artefacto
   - ✅ Modal completo con selector de fase
   - ✅ Campo de razón obligatorio
   - ✅ Tabla de historial de movimientos
   - ✅ Advertencias visuales

4. **`src/app/artifact-uploader/artifact-uploader.component.css`**
   - ✅ Estilos para botón `.btn-reassign` (morado)
   - ✅ Estilos para `.movement-history-section`
   - ✅ Estilos para `.alert-warning`
   - ✅ Estilos para inputs del formulario

---

## Funcionalidad Implementada

### ✅ Criterio 1: Registro de Movimiento
- [x] Cada movimiento se registra en `clArtifactMovements`
- [x] Se guarda: usuario, fecha, razón, fases origen/destino
- [x] Historial completo visible en el modal

### ✅ Criterio 2: Preservación de Historia
- [x] Artefacto mantiene su `_id` (no se duplica)
- [x] Todas las versiones se preservan
- [x] Estados de workflow se mantienen
- [x] Solo se actualiza el campo `phase`

### ✅ Criterio 3: Validación y Confirmación
- [x] Validación: No permitir mover a Transición sin artefactos obligatorios
- [x] Advertencia: Movimientos hacia atrás en el flujo
- [x] Confirmación: Diálogo antes de ejecutar el movimiento
- [x] Razón obligatoria para auditoría

---

## Instrucciones de Configuración

### 1. Ejecutar Script de Inicialización

```bash
cd "c:\Programas\Metodologias\OpenUp Back"
python BackEnd/setup_hu020.py
```

Este script:
- Crea la colección `clArtifactMovements`
- Crea índices para optimizar consultas
- Agrega el permiso `reassign_artifact`

### 2. Verificar Permisos

Asegurarse de que los usuarios tengan el rol apropiado:
- **admin**: Acceso completo
- **product_owner**: Puede reasignar artefactos

### 3. Reiniciar Backend

```bash
# En el directorio OpenUp Back
python Directions.py
```

---

## Pruebas Recomendadas

### Test 1: Movimiento Básico
1. Subir un artefacto en "Incepción"
2. Hacer clic en "Mover"
3. Seleccionar "Elaboración"
4. Ingresar razón: "Corrección de fase"
5. Confirmar
6. ✅ Verificar que aparece en Elaboración

### Test 2: Validación de Transición
1. Intentar mover a "Transición" sin completar obligatorios
2. ✅ Verificar mensaje de error con lista de faltantes
3. Completar artefactos obligatorios
4. Reintentar
5. ✅ Debe permitir el movimiento

### Test 3: Historial de Movimientos
1. Mover un artefacto 2-3 veces
2. Abrir modal de reasignación
3. Clic en "Ver Historial de Movimientos"
4. ✅ Verificar que muestra todos los movimientos con fechas y razones

### Test 4: Preservación de Versiones
1. Subir artefacto v1 en Incepción
2. Subir v2
3. Mover a Elaboración
4. Ir a "Historial" del artefacto
5. ✅ Verificar que v1 y v2 aún existen

---

## Arquitectura

### Flujo de Datos

```
Frontend (artifact-uploader)
    ↓ [click "Mover"]
    ↓
Modal de Reasignación
    ↓ [seleccionar fase + razón]
    ↓
artifact.service.reassignArtifactPhase()
    ↓ HTTP PUT
    ↓
Backend: artifactDirections.reassignArtifactPhase()
    ↓ [verifica permiso 'reassign_artifact']
    ↓
artifactFunctions.fnReassignArtifactPhase()
    ↓ [valida reglas]
    ↓
MongoDB: clArtifacts.update (campo 'phase')
MongoDB: clArtifactMovements.insert (registro de movimiento)
    ↓
Response 200 + data
    ↓
Frontend: Reload artifacts + Success message
```

### Base de Datos

**Colecciones involucradas:**
1. `clArtifacts` - Artefactos (campo `phase` se actualiza)
2. `clArtifactMovements` - Registro de movimientos (nueva)
3. `clPermissions` - Permisos (agrega `reassign_artifact`)

**Índices creados:**
```javascript
clArtifactMovements: { artifactId: 1, movedAt: -1 }
clArtifactMovements: { projectId: 1 }
clArtifactMovements: { movedAt: -1 }
```

---

## Comandos Útiles

### Ver movimientos de un artefacto
```javascript
db.clArtifactMovements.find({ artifactId: "ARTIFACT_ID" }).sort({ movedAt: -1 })
```

### Ver movimientos de un proyecto
```javascript
db.clArtifactMovements.find({ projectId: "P-001" }).sort({ movedAt: -1 })
```

### Estadísticas de movimientos por usuario
```javascript
db.clArtifactMovements.aggregate([
  { $group: { _id: "$movedBy", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Verificar permiso
```javascript
db.clPermissions.findOne({ action: "reassign_artifact" })
```

---

## Archivos de Documentación

- **`HU-020_INSTRUCCIONES.md`** - Documentación técnica completa
- **`BackEnd/setup_hu020.py`** - Script de inicialización
- Este archivo - Resumen ejecutivo

---

## Próximos Pasos Opcionales

1. **Notificaciones**: Notificar al equipo cuando se mueve un artefacto
2. **Dashboard**: Visualizar estadísticas de movimientos
3. **Permisos granulares**: Restricciones por tipo de artefacto
4. **Reversión**: Deshacer último movimiento (admin only)
5. **Movimiento masivo**: Mover múltiples artefactos a la vez

---

## Estado de Archivos

### ✅ Backend
- [x] `BackEnd/Functions/artifactFunctions.py` - 4 nuevas funciones
- [x] `BackEnd/Directions/artifactDirections.py` - 2 nuevos endpoints
- [x] `BackEnd/setup_hu020.py` - Script de inicialización

### ✅ Frontend
- [x] `src/app/service/artifact.service.ts` - 2 nuevos métodos
- [x] `src/app/artifact-uploader/artifact-uploader.component.ts` - 8 nuevos métodos + propiedades
- [x] `src/app/artifact-uploader/artifact-uploader.component.html` - Modal completo + botón
- [x] `src/app/artifact-uploader/artifact-uploader.component.css` - Estilos completos

### ✅ Documentación
- [x] `HU-020_INSTRUCCIONES.md` - Documentación técnica
- [x] `HU-020_RESUMEN.md` - Este archivo

---

## Contacto y Soporte

Para problemas o dudas:
1. Revisar logs del backend (búsqueda: "✅ Artifact")
2. Verificar permisos en `clPermissions`
3. Consultar `HU-020_INSTRUCCIONES.md` para detalles técnicos
4. Ejecutar `setup_hu020.py` si hay problemas de base de datos

---

**Fecha de implementación:** $(Get-Date -Format "yyyy-MM-dd")  
**Versión:** 1.0  
**Estado:** ✅ COMPLETO Y LISTO PARA PRODUCCIÓN
