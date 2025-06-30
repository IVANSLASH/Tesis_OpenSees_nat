# Sistema de Análisis Estructural Modular - OpenSeesPy

## 🏗️ Descripción

Sistema modular y escalable para el modelado y análisis estructural de edificios de varios niveles utilizando OpenSeesPy. El proyecto combina y refactoriza múltiples scripts en una arquitectura modular que permite análisis completos con visualización didáctica y generación de resultados para post-diseño.

## ✨ Características Principales

### 🔧 **Modularidad y Escalabilidad**
- **Arquitectura modular**: Cada funcionalidad en archivos separados
- **Fácil expansión**: Estructura preparada para nuevos elementos (voladizos, escaleras, etc.)
- **Mantenibilidad**: Código bien documentado y organizado

### 📊 **Modelado Completo**
- **Geometría flexible**: Configuración de vanos variables en X/Y y alturas personalizables
- **Elementos estructurales**: Columnas, vigas y losas discretizadas
- **Materiales múltiples**: Concreto, acero, madera con propiedades configurables
- **Secciones personalizables**: Rectangulares y circulares con validación automática

### ⚡ **Cargas y Análisis**
- **Tipos de carga**: Muertas, vivas, puntuales y distribuidas
- **Combinaciones**: Según normativas (LRFD, ASD)
- **Transmisión automática**: Losas → vigas → columnas
- **Análisis robusto**: Con manejo de errores y validaciones

### 🎨 **Visualización Avanzada**
- **Gráficos 3D**: Estructura extruida con secciones reales
- **Deformaciones**: Visualización clara con mallas en losas
- **Diagramas**: Fuerzas internas y momentos
- **Didáctico**: Colores, leyendas y comparaciones

### 📈 **Resultados Completos**
- **Exportación**: Archivos CSV con todas las solicitaciones
- **Organizado**: Por tipo de elemento (columnas, vigas, losas)
- **Post-diseño**: Datos listos para verificación de capacidades

## 🚀 Instalación y Requisitos

### Dependencias
```bash
pip install openseespy
pip install opsvis
pip install matplotlib
pip install numpy
pip install pandas
```

### Verificación de Instalación
```python
import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
print("✅ Todas las dependencias instaladas correctamente")
```

## 📁 Estructura del Proyecto

```
UNSXX_2_OpenseesPy_nativo_GEMINI_Refactored/
├── main.py                 # Script principal orquestador
├── input_data.py           # Gestión de entrada de datos
├── geometry.py             # Creación de nodos y elementos
├── sections.py             # Materiales y secciones transversales
├── slabs.py               # Discretización de losas
├── loads.py               # Cargas y combinaciones
├── analysis.py            # Configuración y ejecución del análisis
├── visualization.py       # Gráficos y visualización 3D
├── results.py             # Extracción y exportación de resultados
├── README.md              # Este archivo
└── Ejemplo de muestra/     # Scripts originales de referencia
    ├── 01.1_Edif_plantas_variables_vanos_var.py
    ├── EJ01.1_Portico3D_planta_vano_variable.py
    └── 02_MEF_automatizado.py
```

## 🎯 Uso del Sistema

### Ejecución Básica
```bash
python main.py
```

### Modos de Operación

#### 1. **Modo Interactivo Completo** 🎛️
- Personalización total de parámetros
- Validación en tiempo real
- Configuración paso a paso

#### 2. **Modo Rápido de Prueba** ⚡
- Valores por defecto optimizados
- Ejecución inmediata
- Ideal para pruebas y demos

#### 3. **Modo por Configuración** 📄
- Carga desde archivos JSON
- Reproducibilidad garantizada
- Ideal para análisis paramétricos

### Ejemplo de Flujo Típico

1. **Seleccionar modo de ejecución**
2. **Configurar geometría**:
   - Número de vanos en X/Y: 3x3
   - Número de pisos: 3
   - Longitudes: 5.0m cada vano
   - Alturas: 3.0m cada piso

3. **Definir materiales**:
   - Concreto f'c=210 kg/cm²
   - Secciones rectangulares

4. **Configurar cargas**:
   - Carga muerta: 4.0 kN/m²
   - Carga viva: 2.0 kN/m²

5. **Ejecutar análisis automático**

6. **Visualizar resultados**

7. **Exportar reportes CSV**

## 📊 Resultados Generados

### Archivos de Salida
- `nodal_displacements.csv`: Desplazamientos nodales
- `element_forces.csv`: Fuerzas en elementos (columnas/vigas)
- `building_config_YYYYMMDD_HHMMSS.json`: Configuración guardada

### Gráficos Generados
1. **Modelo 3D** con estructura completa
2. **Forma deformada** con amplificación
3. **Secciones extruidas** con dimensiones reales
4. **Detalles de secciones** transversales
5. **Comparación** de propiedades geométricas
6. **Diagramas de fuerzas** internas (N, V, M, T)

## ⚙️ Configuración Avanzada

### Archivo de Configuración (JSON)
```json
{
  "num_bay_x": 3,
  "num_bay_y": 3,
  "num_floor": 3,
  "bay_widths_x": [5.0, 6.0, 5.0],
  "bay_widths_y": [4.0, 5.0, 4.0],
  "story_heights": [3.0, 3.0, 3.0],
  "mesh_density": 2
}
```

### Intensidades de Carga
```python
load_intensities = {
    "dead_load_slab": 4.0,     # kN/m²
    "live_load_slab": 2.0,     # kN/m²
    "dead_load_beam": 1.0,     # kN/m
    "live_load_beam": 0.5      # kN/m
}
```

### Materiales Disponibles
- **Concreto f'c=210 kg/cm²** (por defecto)
- **Concreto f'c=280 kg/cm²**
- **Acero ASTM A36**
- **Madera de Pino**

## 🔬 Validación y Verificación

### Rangos Recomendados
- **Vanos**: 3.0 - 15.0 metros
- **Alturas**: 2.5 - 5.0 metros
- **Pisos**: 1 - 20 niveles
- **Cargas losas**: 2.0 - 8.0 kN/m²

### Verificaciones Automáticas
- ✅ Continuidad de nodos
- ✅ Conectividad de elementos
- ✅ Equilibrio de cargas
- ✅ Rangos de parámetros

## 🚀 Expansiones Futuras

### Análisis Avanzado
- [ ] **Análisis sísmico** con espectros de respuesta
- [ ] **Cargas de viento** según normativas
- [ ] **Análisis no lineal** con plasticidad
- [ ] **Análisis dinámico** modal

### Elementos Adicionales
- [ ] **Muros de corte** y pantallas
- [ ] **Voladizos** y elementos especiales
- [ ] **Escaleras** y rampas
- [ ] **Cimentaciones** superficiales y profundas

### Interfaz y Usabilidad
- [ ] **GUI** con tkinter/PyQt
- [ ] **Importación CAD/BIM** (DXF, IFC)
- [ ] **Plantillas** de edificios típicos
- [ ] **Análisis paramétrico** automático

### Diseño y Optimización
- [ ] **Verificación** según normativas
- [ ] **Optimización** automática de secciones
- [ ] **Análisis de costos** materiales
- [ ] **Reportes** profesionales en PDF

## 🔧 Desarrollo y Contribución

### Estructura para Nuevos Módulos
```python
# nuevo_modulo.py
# ============================================
# Descripción clara del módulo y su propósito
# Características principales
# Puntos de escalabilidad
# ============================================

def funcion_principal():
    """Documentación completa con Args, Returns, Examples"""
    pass

# --- Puntos para escalar el código: [Categoría] ---
# - Funcionalidad 1
# - Funcionalidad 2
```

### Mejores Prácticas
1. **Documentación**: Cada función bien documentada
2. **Validación**: Todos los inputs validados
3. **Modularidad**: Funciones enfocadas y reutilizables
4. **Escalabilidad**: Código preparado para expansión
5. **Manejo de errores**: Try-catch apropiados

## 📝 Notas Técnicas

### Sistema de Unidades
- **Longitud**: metros (m)
- **Fuerza**: kilonewtons (kN)
- **Tensión**: kg/cm² (compatible con OpenSeesPy)
- **Masa**: toneladas (ton)

### Limitaciones Actuales
- Elementos frame únicamente (no elementos sólidos)
- Análisis estático lineal
- Materiales elásticos lineales
- Cargas estáticas únicamente

### Rendimiento
- **Modelos pequeños** (≤5 pisos, ≤10 vanos): < 10 segundos
- **Modelos medianos** (5-10 pisos, 10-20 vanos): < 30 segundos
- **Modelos grandes** (>10 pisos, >20 vanos): Verificar recursos

## 📞 Soporte

### Resolución de Problemas
1. **Verificar instalación** de OpenSeesPy y dependencias
2. **Revisar rangos** de parámetros de entrada
3. **Consultar mensajes** de error detallados
4. **Verificar recursos** del sistema para modelos grandes

### Contacto y Documentación
- Documentación OpenSeesPy: [opensees.berkeley.edu](https://opensees.berkeley.edu)
- Ejemplos adicionales en la carpeta `Ejemplo de muestra/`
- Issues y mejoras: Crear en el repositorio del proyecto

---

**🎯 Objetivo**: Proporcionar una herramienta robusta, didáctica y escalable para el análisis estructural de edificios, facilitando el aprendizaje y la aplicación práctica de OpenSeesPy en proyectos reales.

**🔄 Versión**: 2.0 - Sistema Modular Refactorizado

**📅 Última actualización**: 2025
