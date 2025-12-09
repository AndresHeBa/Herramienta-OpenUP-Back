# Pruebas Rápidas - HU-020: Reasignar Artefactos

## Prueba 1: Verificar Endpoints

### Backend activo
```bash
# Verificar que el servidor está corriendo
curl http://localhost:5000/api/artifacts/getArtifactTypes
```

### Verificar permiso (con autenticación)
```bash
# Debería retornar 401 o 403 sin autenticación válida
curl -X PUT http://localhost:5000/api/artifacts/reassignPhase/ARTIFACT_ID \
  -H "Content-Type: application/json" \
  -H "X-User-Roles: admin" \
  -d '{
    "newPhase": "Elaboración",
    "userId": "admin_user",
    "reason": "Prueba de endpoint"
  }'
```

---

## Prueba 2: Interfaz Frontend

### Pasos en el navegador

1. **Abrir proyecto**
   - Ir a "Proyectos" → Seleccionar proyecto → "Ver" → "Abrir Artefactos"
   - URL: `http://localhost:4200/artifacts/P-001` (ajustar según proyecto)

2. **Verificar botón "Mover"**
   - ✅ Botón "Mover" debe aparecer en cada fila de artefacto
   - ✅ Botón deshabilitado si no hay artefacto subido
   - ✅ Color morado distintivo

3. **Abrir modal de reasignación**
   - Clic en "Mover"
   - ✅ Modal aparece con título correcto
   - ✅ Muestra fase actual
   - ✅ Selector de fase destino (excluye fase actual)
   - ✅ Campo de razón vacío

4. **Ver historial de movimientos**
   - Clic en "Ver Historial de Movimientos"
   - ✅ Si no hay movimientos: "No hay movimientos previos registrados"
   - ✅ Si hay movimientos: tabla con columnas (Desde, Hacia, Movido por, Fecha, Razón)

5. **Ejecutar reasignación**
   - Seleccionar fase destino
   - Ingresar razón: "Prueba de reasignación"
   - Clic en "Confirmar Movimiento"
   - ✅ Diálogo de confirmación aparece
   - Confirmar
   - ✅ Mensaje de éxito
   - ✅ Artefacto desaparece de fase actual
   - Cambiar a fase destino
   - ✅ Artefacto aparece en nueva fase

6. **Verificar preservación de versiones**
   - En nueva fase, clic en "Historial" del artefacto movido
   - ✅ Todas las versiones previas deben estar presentes
   - ✅ Fechas y autores se mantienen

---

## Prueba 3: Validaciones

### Validación 1: Razón obligatoria
1. Abrir modal de reasignación
2. Seleccionar fase destino
3. Dejar razón vacía
4. Clic en "Confirmar Movimiento"
5. ✅ Error: "Debe proporcionar una razón para el movimiento"

### Validación 2: Bloqueo de Transición sin obligatorios
1. Crear proyecto nuevo con solo artefactos opcionales
2. Intentar mover a "Transición"
3. ✅ Error: "Cannot move to Transition: Missing mandatory artifacts - [lista]"
4. ✅ Lista muestra artefactos obligatorios faltantes

### Validación 3: Advertencia de movimiento hacia atrás
1. Mover artefacto de "Construcción" a "Elaboración"
2. ✅ Advertencia aparece: "⚠️ Advertencia: ... Moving backwards..."
3. ✅ Permite continuar después de confirmación

---

## Prueba 4: MongoDB

### Verificar colección creada
```javascript
// En MongoDB Compass o shell
use openup_db  // o tu nombre de base de datos

// Ver colecciones
show collections
// Debe incluir: clArtifactMovements

// Ver documentos
db.clArtifactMovements.find().pretty()
```

### Verificar índices
```javascript
db.clArtifactMovements.getIndexes()
// Debe mostrar:
// - _id_
// - idx_artifact_movements (artifactId + movedAt)
// - idx_project_movements (projectId)
// - idx_movement_date (movedAt)
```

### Verificar permiso
```javascript
db.clPermissions.find({ action: "reassign_artifact" }).pretty()
// Debe mostrar:
// {
//   action: "reassign_artifact",
//   roles: ["admin", "product_owner"],
//   createdAt: ISODate(...)
// }
```

---

## Prueba 5: Logs del Backend

### Buscar en consola del backend

Después de realizar una reasignación, buscar:

```
✅ Artifact [tipo] moved from [fase_origen] to [fase_destino] by [usuario]
```

### Logs esperados
```
🔍 Getting configuration for project: P-001
✅ Artifact Documento de Visión moved from Incepción to Elaboración by admin_user
```

---

## Prueba 6: Historial de Movimientos

### Movimientos múltiples
1. Mover artefacto de Incepción → Elaboración (razón: "Primera corrección")
2. Mover de Elaboración → Construcción (razón: "Segunda corrección")
3. Mover de Construcción → Elaboración (razón: "Retroceso necesario")
4. Abrir modal y ver historial
5. ✅ Debe mostrar 3 movimientos ordenados por fecha (más reciente primero)

### Verificar datos de movimiento
Para cada movimiento en la tabla:
- ✅ Columna "Desde" muestra fase origen correcta
- ✅ Columna "Hacia" muestra fase destino correcta
- ✅ Columna "Movido por" muestra usuario
- ✅ Columna "Fecha" muestra timestamp formateado
- ✅ Columna "Razón" muestra texto ingresado

---

## Prueba 7: Permisos

### Usuario sin permiso
1. Cambiar roles del usuario (remover 'admin' y 'product_owner')
2. Intentar acceder a reasignación
3. ✅ Debe mostrar error 403: "No tiene permiso para 'reassign_artifact'"

### Usuario con permiso admin
1. Asegurar que usuario tiene rol 'admin'
2. Ejecutar reasignación
3. ✅ Debe funcionar sin restricciones

### Usuario con permiso product_owner
1. Usuario con rol 'product_owner' pero no 'admin'
2. Ejecutar reasignación
3. ✅ Debe funcionar correctamente

---

## Checklist Final

### Backend
- [ ] Servidor backend corriendo sin errores
- [ ] Colección `clArtifactMovements` existe
- [ ] Índices creados correctamente
- [ ] Permiso `reassign_artifact` existe
- [ ] Endpoints responden correctamente

### Frontend
- [ ] Botón "Mover" visible en cada artefacto
- [ ] Modal se abre correctamente
- [ ] Selector de fases funciona
- [ ] Campo de razón valida entrada
- [ ] Historial de movimientos se muestra
- [ ] Confirmación antes de ejecutar
- [ ] Mensajes de éxito/error aparecen

### Funcionalidad
- [ ] Artefacto se mueve entre fases
- [ ] Versiones se preservan
- [ ] Estados de workflow se mantienen
- [ ] Movimientos se registran en DB
- [ ] Validaciones funcionan
- [ ] Advertencias aparecen cuando corresponde

### Base de Datos
- [ ] Documentos en `clArtifactMovements` después de mover
- [ ] Campo `phase` actualizado en `clArtifacts`
- [ ] Todas las versiones preservadas
- [ ] Consultas de historial rápidas (índices funcionando)

---

## Comandos de Ayuda

### Reiniciar backend
```bash
cd "c:\Programas\Metodologias\OpenUp Back"
python Directions.py
```

### Reiniciar frontend
```bash
cd "c:\Programas\Metodologias\OpenUP Front\OpenUP"
npm start
```

### Ver logs en tiempo real (PowerShell)
```powershell
# Backend
cd "c:\Programas\Metodologias\OpenUp Back"
python Directions.py | Select-String -Pattern "Artifact|moved|reassign"

# Frontend (console del navegador)
# F12 → Console → filtrar por "Artifact" o "reassign"
```

### Limpiar datos de prueba
```javascript
// Eliminar movimientos de prueba
db.clArtifactMovements.deleteMany({ reason: /prueba/i })

// O restaurar fase original de un artefacto
db.clArtifacts.updateOne(
  { _id: ObjectId("ARTIFACT_ID") },
  { $set: { phase: "Incepción" } }
)
```

---

## Resultados Esperados

### ✅ Éxito total si:
- Todos los puntos del checklist están marcados
- Artefactos se mueven sin perder datos
- Historial de movimientos se registra correctamente
- Validaciones bloquean movimientos incorrectos
- Interfaz responde sin errores

### ⚠️ Revisión necesaria si:
- Errores 403 con usuarios autorizados → Verificar roles
- Artefacto no aparece en nueva fase → Verificar logs backend
- Historial vacío después de mover → Verificar colección MongoDB
- Modal no abre → Verificar errores en console del navegador

### ❌ Falla crítica si:
- Backend arroja excepciones al reasignar
- Artefacto desaparece después de mover
- Versiones se pierden
- Permiso no funciona para admin

---

**Duración estimada de pruebas completas:** 15-20 minutos

**Prioridad de pruebas:**
1. Alta: Prueba 2 (Interfaz), Prueba 3 (Validaciones), Prueba 6 (Historial)
2. Media: Prueba 4 (MongoDB), Prueba 5 (Logs)
3. Baja: Prueba 7 (Permisos - solo si hay múltiples roles)
