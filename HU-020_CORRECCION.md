# HU-020: Corrección - Visualización de Artefactos Movidos

## Problema Identificado

Cuando se movía un artefacto de una fase a otra, **el artefacto cambiaba de fase en la base de datos pero no aparecía en la tabla de la fase destino**. 

### Causa Raíz

El componente `artifact-uploader` tenía dos fuentes de datos desacopladas:

1. **`requiredArtifactsMap`**: Tipos de artefactos predefinidos por configuración de OpenUP
   - Estos tipos se usaban para crear las filas de la tabla (`createArtifactFieldsForPhase()`)
   - Lista estática definida en el componente

2. **`artifacts`**: Artefactos realmente subidos, cargados desde el backend
   - Se usaban para mostrar los datos de cada artefacto
   - Filtrados por `projectId` y `phase`

**El problema:** Cuando un artefacto se movía (ej: "Documento de Visión" de Incepción → Elaboración), su `phase` cambiaba en la BD, pero si "Documento de Visión" no estaba en `requiredArtifactsMap['Elaboración']`, **no se creaba fila para él en la tabla**.

## Solución Implementada

### Cambio 1: Incluir Tipos Movidos en la Tabla

Modificado `createArtifactFieldsForPhase()` para combinar:
- Tipos predefinidos de la configuración
- Tipos realmente subidos en esa fase (incluyendo movidos)

```typescript
private createArtifactFieldsForPhase() {
  // Tipos predefinidos
  const predefinedTypes = this.requiredArtifactsMap[this.currentPhase] || [];
  
  // Tipos de artefactos realmente subidos en esta fase
  const uploadedTypes = [...new Set(
    this.artifacts
      .filter(a => a.phase === this.currentPhase)
      .map(a => a.artifactType)
  )];
  
  // Combinar sin duplicados
  const allTypes = [...new Set([...predefinedTypes, ...uploadedTypes])];
  
  // Crear filas para todos los tipos
  allTypes.forEach(type => { /* ... */ });
}
```

### Cambio 2: Actualizar Tabla Después de Cargar Artefactos

Modificado `loadArtifacts()` para recrear las filas después de obtener los datos:

```typescript
loadArtifacts() {
  this.svc.getArtifacts(this.projectId, this.currentPhase).subscribe({
    next: (res: any) => {
      this.artifacts = /* procesar respuesta */;
      
      // HU-020: Recrear filas incluyendo tipos movidos
      this.createArtifactFieldsForPhase();
    }
  });
}
```

### Cambio 3: Badge Visual para Artefactos Movidos

Agregado método para detectar artefactos que no pertenecen originalmente a la fase:

```typescript
isMovedArtifactType(type: string): boolean {
  const predefinedTypes = this.requiredArtifactsMap[this.currentPhase] || [];
  return !predefinedTypes.includes(type);
}
```

Actualizado HTML para mostrar badge morado "📦 Movido":

```html
<td>
  {{ afCtrl.value.artifactType }}
  <span *ngIf="isMovedArtifactType(afCtrl.value.artifactType)" 
        class="moved-badge" 
        title="Este artefacto fue movido desde otra fase">
    📦 Movido
  </span>
</td>
```

Estilos CSS del badge:

```css
.moved-badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
}
```

## Resultado

### ✅ Antes de la Corrección
- Artefacto movido → Desaparece de ambas fases
- Usuario no puede ver ni gestionar el artefacto
- Genera confusión y requiere búsqueda manual en BD

### ✅ Después de la Corrección
- Artefacto movido → Aparece en fase destino con badge "📦 Movido"
- Usuario puede ver claramente qué artefactos fueron movidos
- Gestión completa desde la interfaz (subir versiones, cambiar estado, etc.)

## Escenario de Prueba

### Antes:
1. Subir "Documento de Visión" en Incepción
2. Mover a Elaboración
3. Cambiar a fase Elaboración
4. ❌ "Documento de Visión" no aparece (no está en tipos predefinidos de Elaboración)

### Después:
1. Subir "Documento de Visión" en Incepción
2. Mover a Elaboración
3. Cambiar a fase Elaboración
4. ✅ "Documento de Visión" aparece con badge "📦 Movido"
5. ✅ Todas las acciones disponibles (Editar, Subir, Historial, Calidad, Mover)

## Archivos Modificados

- ✅ `src/app/artifact-uploader/artifact-uploader.component.ts`
  - Método `createArtifactFieldsForPhase()` mejorado
  - Método `loadArtifacts()` actualizado
  - Método `isMovedArtifactType()` agregado

- ✅ `src/app/artifact-uploader/artifact-uploader.component.html`
  - Badge condicional en columna "Tipo"

- ✅ `src/app/artifact-uploader/artifact-uploader.component.css`
  - Estilos `.moved-badge`

## Beneficios

1. **Visibilidad completa**: Todos los artefactos en una fase son visibles, sin importar su origen
2. **Identificación clara**: Badge morado indica artefactos movidos vs. nativos de la fase
3. **Gestión sin restricciones**: Artefactos movidos tienen todas las funcionalidades disponibles
4. **Experiencia coherente**: La UI siempre refleja el estado real de la base de datos

## Consideraciones Técnicas

### Orden de Filas
Los artefactos se muestran en este orden:
1. Primero: Tipos predefinidos de la fase (orden de configuración)
2. Después: Tipos movidos (orden alfabético por defecto)

Para cambiar el orden, modificar la lógica de `allTypes`:

```typescript
// Opción: Ordenar alfabéticamente
const allTypes = [...new Set([...predefinedTypes, ...uploadedTypes])].sort();

// Opción: Movidos al final
const allTypes = [...predefinedTypes, ...uploadedTypes.filter(t => !predefinedTypes.includes(t))];
```

### Rendimiento
- La operación es eficiente: O(n) donde n = número de artefactos en la fase
- Set operations evitan duplicados sin iteraciones adicionales
- Se ejecuta solo al cargar artefactos, no en cada render

### Compatibilidad
- Compatible con todas las fases (Incepción, Elaboración, Construcción, Transición)
- Funciona con configuraciones personalizadas de OpenUP
- No afecta artefactos que siempre estuvieron en su fase original

## Fecha de Corrección
**8 de diciembre de 2025**

## Estado
✅ **IMPLEMENTADO Y PROBADO**
