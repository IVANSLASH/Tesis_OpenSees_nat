# Copyright (c) 2025, OpenSeesPy IvanSlashlopers

# -----------------------------------------------------------------------------
#  RESUMEN DEL SCRIPT
# -----------------------------------------------------------------------------
#  Este programa interactivo genera un pórtico tridimensional en OpenSeesPy a
#  partir de parámetros introducidos por el usuario (vanos en X y Y, pisos,
#  longitudes y alturas).  En sistema métrico, calcula la malla ortogonal y
#  crea 60 nodos (15 por nivel en 4 niveles, contando la base), mostrando un
#  listado exhaustivo de numeración y coordenadas para verificación.
#
#  Tras validar que el número de nodos creados coincide con el esperado,
#  intenta formar columnas y vigas: construye correctamente 45 columnas,
#  pero solo 18 vigas en la dirección Y, porque la comprobación de alineación
#  detecta desajustes geométricos que impiden crear vigas en dirección X.
#  Cada inconsistencia se reporta con mensajes de ERROR que facilitan la
#  depuración de la geometría ingresada.
#
#  Una vez definidos los elementos (total 63), aplica una carga puntual de
#  1 kN en la dirección X sobre el nodo inicial del último nivel y ejecuta
#  un análisis estático lineal.  Al no especificarse algoritmos ni sistemas,
#  OpenSees emplea los valores por defecto y emite advertencias, lo que no
#  compromete la ejecución pero recuerda que pueden elegirse opciones más
#  adecuadas.
#
#  Finalmente presenta un resumen por nivel y lanza la visualización del
#  modelo, completando un flujo que va desde la entrada paramétrica hasta la
#  evaluación estructural preliminar con diagnóstico detallado.
# -----------------------------------------------------------------------------

# All rights reserved.
# Automatiza la creacion de vigas y columnas pero falla en la cracion de vigas en la ultima losa

# =============================================================================
# DEFINICIÓN DEL SISTEMA DE UNIDADES (SISTEMA MÉTRICO)
# =============================================================================
# Unidades de longitud: metros (m)
# Unidades de fuerza: kilonewtons (kN)
# Unidades de tiempo: segundos (s)
# Unidades de masa: toneladas (ton) - 1 ton = 1000 kg
# Unidades de presión/tensión: kilopascales (kPa) - 1 kPa = 1 kN/m²
# Unidades de módulo de elasticidad: megapascales (MPa) - 1 MPa = 1000 kPa
# 
# Conversiones importantes:
# - 1 ton-fuerza = 9.81 kN (aproximadamente 10 kN para cálculos prácticos)
# - 1 MPa = 1000 kPa = 1000 kN/m²
# =============================================================================

# Importar librerías necesarias
import opsvis as opsvis  # Librería para visualización de modelos OpenSeesPy
import openseespy.opensees as ops  # Librería principal de OpenSeesPy
import matplotlib.pyplot as plt  # Librería para gráficos
import numpy as np  # Librería para cálculos numéricos
from math import asin  # Función matemática (no se usa en este código)

# Limpiar cualquier modelo anterior y crear uno nuevo
ops.wipe()  # Limpiar el modelo anterior
ops.model('Basic', '-ndm', 3, '-ndf', 6)  # Crear modelo 3D con 6 grados de libertad por nodo

# =============================================================================
# ENTRADA DE DATOS GEOMÉTRICOS DEL EDIFICIO
# =============================================================================
print("=== CONFIGURACIÓN GEOMÉTRICA DEL EDIFICIO ===")

# Número de vanos y pisos
numBayX = int(input("Ingrese el número de vanos en dirección X: "))  # Solicitar número de vanos en X
numBayY = int(input("Ingrese el número de vanos en dirección Y: "))  # Solicitar número de vanos en Y
numFloor = int(input("Ingrese el número de pisos: "))  # Solicitar número de pisos

# Entrada manual de longitudes de vanos en dirección X
print(f"\n--- Longitudes de vanos en dirección X ---")
bayWidthsX = []  # Lista para almacenar longitudes de vanos X
for i in range(numBayX):  # Bucle para cada vano en dirección X
    longitud = float(input(f"Ingrese la longitud del vano {i+1} en dirección X (metros): "))  # Solicitar longitud
    bayWidthsX.append(longitud)  # Agregar longitud a la lista

# Entrada manual de longitudes de vanos en dirección Y
print(f"\n--- Longitudes de vanos en dirección Y ---")
bayWidthsY = []  # Lista para almacenar longitudes de vanos Y
for j in range(numBayY):  # Bucle para cada vano en dirección Y
    longitud = float(input(f"Ingrese la longitud del vano {j+1} en dirección Y (metros): "))  # Solicitar longitud
    bayWidthsY.append(longitud)  # Agregar longitud a la lista

# Alturas de pisos
print(f"\n--- Alturas de pisos ---")
storyHeights = []  # Lista para almacenar alturas de pisos
for k in range(numFloor):  # Bucle para cada piso
    altura = float(input(f"Ingrese la altura del piso {k+1} (metros): "))  # Solicitar altura
    storyHeights.append(altura)  # Agregar altura a la lista

# =============================================================================
# PROPIEDADES DE MATERIALES (en unidades métricas)
# =============================================================================
E = 29500  # Módulo de elasticidad del material (MPa)
massX = 0.49  # Masa en dirección X (ton)
M = 0  # Masa adicional para elementos (ton)
coordTransf = "Linear"  # Tipo de transformación de coordenadas
massType = "-lMass"  # Tipo de masa (masa distribuida)

print(f"\n=== RESUMEN DE CONFIGURACIÓN ===")
print(f"Número de vanos X: {numBayX}")  # Mostrar número de vanos X
print(f"Número de vanos Y: {numBayY}")  # Mostrar número de vanos Y
print(f"Número de pisos: {numFloor}")  # Mostrar número de pisos
print(f"Longitudes vanos X: {bayWidthsX} metros")  # Mostrar longitudes de vanos X
print(f"Longitudes vanos Y: {bayWidthsY} metros")  # Mostrar longitudes de vanos Y
print(f"Alturas de pisos: {storyHeights} metros")  # Mostrar alturas de pisos
print(f"Módulo de elasticidad: {E} MPa")  # Mostrar módulo de elasticidad

print("\n=== GENERACIÓN DE NODOS ===")

# Inicializar variables para la generación de nodos
nodeTag = 1  # Contador de tags de nodos
zLoc = 0  # Coordenada Z inicial (nivel base)
total_nodos = 0  # Contador total de nodos creados

# CORRECCIÓN: Bucle principal para generar todos los nodos del edificio
# Los nodos se generan por filas (Y) y columnas (X) para cada nivel
for k in range(numFloor + 1):  # Para cada nivel (incluyendo base)
    zLoc = 0  # Coordenada Z inicial para este nivel
    if k > 0:  # Si no es el nivel base, calcular altura acumulada
        for piso in range(k):  # Bucle para calcular altura acumulada
            zLoc += storyHeights[piso]  # Sumar altura del piso
    
    # Generar nodos por filas (Y) y columnas (X)
    for j in range(numBayY + 1):  # Para cada fila en dirección Y
        yLoc = 0  # Coordenada Y inicial para esta fila
        if j > 0:  # Calcular posición Y acumulada
            for vano in range(j):  # Bucle para calcular posición Y
                yLoc += bayWidthsY[vano]  # Sumar longitud del vano
        
        for i in range(numBayX + 1):  # Para cada columna en dirección X
            xLoc = 0  # Coordenada X inicial para esta columna
            if i > 0:  # Calcular posición X acumulada
                for vano in range(i):  # Bucle para calcular posición X
                    xLoc += bayWidthsX[vano]  # Sumar longitud del vano
            
            # Crear nodo con coordenadas calculadas
            ops.node(nodeTag, xLoc, yLoc, zLoc)  # Crear nodo con coordenadas (x,y,z)
            ops.mass(nodeTag, massX, massX, 0.01, 1.0e-10, 1.0e-10, 1e-10)  # Asignar masa al nodo

            if k == 0:  # Si es el nivel base (k=0)
                ops.fix(nodeTag, 1, 1, 1, 1, 1, 1)  # Empotrar el nodo en todos los grados de libertad

            nodeTag += 1  # Incrementar tag del nodo
            total_nodos += 1  # Incrementar contador total

print(f"Total de nodos creados: {total_nodos}")  # Mostrar total de nodos creados

# =============================================================================
# VERIFICACIÓN: Calcular nodos esperados vs creados
# =============================================================================
nodos_por_nivel = (numBayX + 1) * (numBayY + 1)  # Calcular nodos por nivel
total_nodos_esperados = (numFloor + 1) * nodos_por_nivel  # Calcular total esperado
print(f"\n=== VERIFICACIÓN DE NODOS ===")
print(f"Nodos por nivel: {nodos_por_nivel}")  # Mostrar nodos por nivel
print(f"Total de niveles: {numFloor + 1}")  # Mostrar total de niveles
print(f"Total de nodos esperados: {total_nodos_esperados}")  # Mostrar total esperado
print(f"Total de nodos creados: {total_nodos}")  # Mostrar total creado
if total_nodos != total_nodos_esperados:  # Verificar si coinciden
    print(f"⚠️  ADVERTENCIA: Diferencia en número de nodos!")  # Mostrar advertencia

# =============================================================================
# DEPURACIÓN: Verificar numeración de nodos por nivel
# =============================================================================
print("\n=== DEPURACIÓN: NUMERACIÓN DE NODOS ===")
for k in range(numFloor + 1):  # Para cada nivel
    print(f"\nNivel {k}:")  # Mostrar número de nivel
    nodo_inicial = 1 + k * nodos_por_nivel  # Calcular nodo inicial del nivel
    print(f"  Nodo inicial del nivel: {nodo_inicial}")  # Mostrar nodo inicial
    for j in range(numBayY + 1):  # Para cada fila Y
        fila = []  # Lista para almacenar nodos de la fila
        for i in range(numBayX + 1):  # Para cada columna X
            nodeTag = nodo_inicial + j * (numBayX + 1) + i  # Calcular tag del nodo
            if nodeTag <= total_nodos:  # Si el nodo existe
                coord = ops.nodeCoord(nodeTag)  # Obtener coordenadas del nodo
                fila.append(f"N{nodeTag}({coord[0]:.1f},{coord[1]:.1f},{coord[2]:.1f})")  # Agregar nodo a la fila
            else:  # Si el nodo no existe
                fila.append(f"N{nodeTag}(NO_EXISTE)")  # Indicar que no existe
        print(f"  Fila {j}: {' | '.join(fila)}")  # Mostrar fila completa

# =============================================================================
# VERIFICACIÓN ADICIONAL: Mostrar conexiones esperadas
# =============================================================================
print("\n=== VERIFICACIÓN: CONEXIONES ESPERADAS ===")
for k in range(1, numFloor + 1):  # Solo niveles con vigas
    print(f"\nNivel {k} - Conexiones esperadas:")  # Mostrar nivel
    nodo_inicial = 1 + k * nodos_por_nivel  # Calcular nodo inicial del nivel
    
    # Vigas X esperadas
    print("  Vigas X (horizontales):")  # Mostrar título para vigas X
    for j in range(numBayY + 1):  # Para cada fila Y
        nodo_fila = nodo_inicial + j * (numBayX + 1)  # Calcular nodo inicial de la fila
        for i in range(numBayX):  # Para cada vano en dirección X
            n1 = nodo_fila + i  # Nodo inicial de la viga
            n2 = n1 + 1  # Nodo final de la viga
            if n1 <= total_nodos and n2 <= total_nodos:  # Si ambos nodos existen
                coord1 = ops.nodeCoord(n1)  # Obtener coordenadas del nodo inicial
                coord2 = ops.nodeCoord(n2)  # Obtener coordenadas del nodo final
                print(f"    Nodo {n1}({coord1[0]:.1f},{coord1[1]:.1f}) -> Nodo {n2}({coord2[0]:.1f},{coord2[1]:.1f})")  # Mostrar conexión
    
    # Vigas Y esperadas
    print("  Vigas Y (verticales):")  # Mostrar título para vigas Y
    for i in range(numBayX + 1):  # Para cada columna X
        for j in range(numBayY):  # Para cada vano en dirección Y
            n1 = nodo_inicial + j * (numBayX + 1) + i  # Nodo inicial de la viga
            n2 = n1 + (numBayX + 1)  # Nodo final de la viga
            if n1 <= total_nodos and n2 <= total_nodos:  # Si ambos nodos existen
                coord1 = ops.nodeCoord(n1)  # Obtener coordenadas del nodo inicial
                coord2 = ops.nodeCoord(n2)  # Obtener coordenadas del nodo final
                print(f"    Nodo {n1}({coord1[0]:.1f},{coord1[1]:.1f}) -> Nodo {n2}({coord2[0]:.1f},{coord2[1]:.1f})")  # Mostrar conexión

# Definir transformaciones geométricas para elementos
ops.geomTransf(coordTransf, 1, 1, 0, 0)  # Transformación para columnas (eje Y)
ops.geomTransf(coordTransf, 2, 0, 0, 1)  # Transformación para vigas (eje Z)

print("=== GENERACIÓN DE COLUMNAS ===")

# Inicializar variables para la generación de columnas
eleTag   = 1  # Contador de tags de elementos
nodeTag1 = 1  # Nodo inicial (base)
total_columnas = 0  # Contador de columnas creadas

# Bucle para generar todas las columnas
for k in range(0, numFloor):  # Para cada nivel (excepto el último)
    for i in range(0, numBayX+1):  # Para cada posición X
        for j in range(0, numBayY+1):  # Para cada posición Y
            nodeTag2 = nodeTag1 + (numBayX+1)*(numBayY+1)  # Nodo superior de la columna
            iNode    = ops.nodeCoord(nodeTag1)  # Coordenadas del nodo inferior
            jNode    = ops.nodeCoord(nodeTag2)  # Coordenadas del nodo superior
            ops.element(  # Crear elemento columna
                'elasticBeamColumn', eleTag,  # Tipo de elemento
                nodeTag1, nodeTag2,  # Nodos conectados
                50, E, 1000, 1000, 2150, 2150, 1,  # Propiedades: A, E, Iz, Iy, J, G, transfTag
                '-mass', M, massType  # Propiedades de masa
            )
            eleTag   += 1  # Incrementar tag del elemento
            nodeTag1 += 1  # Pasar al siguiente nodo base
            total_columnas += 1  # Incrementar contador

print(f"Total de columnas creadas: {total_columnas}")  # Mostrar total de columnas

print("=== GENERACIÓN DE VIGAS DIRECCIÓN X ===")

# CORRECCIÓN: Generación correcta de vigas en dirección X (ortogonales)
# Las vigas en dirección X conectan nodos adyacentes en la misma fila Y
total_vigas_x = 0  # Contador de vigas X

print("  Creando vigas en dirección X (horizontal):")  # Mostrar mensaje de inicio
for k in range(1, numFloor + 1):  # Para cada nivel (desde primer piso hasta último)
    # Calcular el nodo inicial del nivel k
    nodos_por_nivel = (numBayX + 1) * (numBayY + 1)  # Calcular nodos por nivel
    nodo_inicial_nivel = 1 + k * nodos_por_nivel  # Calcular nodo inicial del nivel
    
    print(f"    Nivel {k}: Nodo inicial = {nodo_inicial_nivel}")  # Mostrar información del nivel
    
    # Recorrer cada fila Y del nivel
    for j in range(numBayY + 1):  # Para cada fila en dirección Y
        # Calcular el nodo inicial de esta fila
        nodo_inicial_fila = nodo_inicial_nivel + j * (numBayX + 1)  # Calcular nodo inicial de la fila
        
        # Conectar nodos adyacentes en esta fila (dirección X)
        for i in range(numBayX):  # Para cada vano en dirección X
            nodeTag1 = nodo_inicial_fila + i  # Nodo inicial de la viga
            nodeTag2 = nodeTag1 + 1  # Nodo final de la viga
            
            # Verificar que ambos nodos existen
            if nodeTag1 <= total_nodos and nodeTag2 <= total_nodos:  # Si ambos nodos existen
                # Verificar que los nodos están en la misma fila (misma Y)
                coord1 = ops.nodeCoord(nodeTag1)  # Obtener coordenadas del nodo inicial
                coord2 = ops.nodeCoord(nodeTag2)  # Obtener coordenadas del nodo final
                if abs(coord1[1] - coord2[1]) < 0.001:  # Misma coordenada Y (tolerancia)
                    ops.element(  # Crear elemento viga
                        'elasticBeamColumn', eleTag,  # Tipo de elemento
                        nodeTag1, nodeTag2,  # Nodos conectados
                        50, E, 1000, 1000, 2150, 2150, 2,  # Propiedades: A, E, Iz, Iy, J, G, transfTag
                        '-mass', M, massType  # Propiedades de masa
                    )
                    print(f"      Viga X {eleTag}: Nodo {nodeTag1}({coord1[0]:.1f},{coord1[1]:.1f},{coord1[2]:.1f}) -> Nodo {nodeTag2}({coord2[0]:.1f},{coord2[1]:.1f},{coord2[2]:.1f})")  # Mostrar viga creada
                    eleTag += 1  # Incrementar tag del elemento
                    total_vigas_x += 1  # Incrementar contador
                else:  # Si los nodos no están en la misma fila
                    print(f"      ERROR: Nodos {nodeTag1} y {nodeTag2} no están en la misma fila Y")  # Mostrar error
            else:  # Si alguno de los nodos no existe
                print(f"      ERROR: Nodos {nodeTag1} o {nodeTag2} no existen (total: {total_nodos})")  # Mostrar error

print(f"Total de vigas en dirección X creadas: {total_vigas_x}")  # Mostrar total de vigas X

print("=== GENERACIÓN DE VIGAS DIRECCIÓN Y ===")

# CORRECCIÓN: Generación correcta de vigas en dirección Y (ortogonales)
# Las vigas en dirección Y conectan nodos adyacentes en la misma columna X
total_vigas_y = 0  # Contador de vigas Y

print("  Creando vigas en dirección Y (vertical en planta):")  # Mostrar mensaje de inicio
for k in range(1, numFloor + 1):  # Para cada nivel (desde primer piso hasta último)
    # Calcular el nodo inicial del nivel k
    nodos_por_nivel = (numBayX + 1) * (numBayY + 1)  # Calcular nodos por nivel
    nodo_inicial_nivel = 1 + k * nodos_por_nivel  # Calcular nodo inicial del nivel
    
    print(f"    Nivel {k}: Nodo inicial = {nodo_inicial_nivel}")  # Mostrar información del nivel
    
    # Recorrer cada columna X del nivel
    for i in range(numBayX + 1):  # Para cada columna en dirección X
        # Conectar nodos adyacentes en esta columna (dirección Y)
        for j in range(numBayY):  # Para cada vano en dirección Y
            nodeTag1 = nodo_inicial_nivel + j * (numBayX + 1) + i  # Nodo inicial de la viga
            nodeTag2 = nodeTag1 + (numBayX + 1)  # Nodo final de la viga
            
            # Verificar que ambos nodos existen
            if nodeTag1 <= total_nodos and nodeTag2 <= total_nodos:  # Si ambos nodos existen
                # Verificar que los nodos están en la misma columna (misma X)
                coord1 = ops.nodeCoord(nodeTag1)  # Obtener coordenadas del nodo inicial
                coord2 = ops.nodeCoord(nodeTag2)  # Obtener coordenadas del nodo final
                if abs(coord1[0] - coord2[0]) < 0.001:  # Misma coordenada X (tolerancia)
                    ops.element(  # Crear elemento viga
                        'elasticBeamColumn', eleTag,  # Tipo de elemento
                        nodeTag1, nodeTag2,  # Nodos conectados
                        50, E, 1000, 1000, 2150, 2150, 2,  # Propiedades: A, E, Iz, Iy, J, G, transfTag
                        '-mass', M, massType  # Propiedades de masa
                    )
                    print(f"      Viga Y {eleTag}: Nodo {nodeTag1}({coord1[0]:.1f},{coord1[1]:.1f},{coord1[2]:.1f}) -> Nodo {nodeTag2}({coord2[0]:.1f},{coord2[1]:.1f},{coord2[2]:.1f})")  # Mostrar viga creada
                    eleTag += 1  # Incrementar tag del elemento
                    total_vigas_y += 1  # Incrementar contador
                else:  # Si los nodos no están en la misma columna
                    print(f"      ERROR: Nodos {nodeTag1} y {nodeTag2} no están en la misma columna X")  # Mostrar error
            else:  # Si alguno de los nodos no existe
                print(f"      ERROR: Nodos {nodeTag1} o {nodeTag2} no existen (total: {total_nodos})")  # Mostrar error

print(f"Total de vigas en dirección Y creadas: {total_vigas_y}")  # Mostrar total de vigas Y

# Calcular total de elementos
total_elementos = total_columnas + total_vigas_x + total_vigas_y  # Calcular total de elementos
print(f"Total de elementos creados: {total_elementos}")  # Mostrar total de elementos

# Verificar nodos en diferentes niveles para depuración
print("\n=== VERIFICACIÓN DE NODOS POR NIVEL ===")
for k in range(numFloor + 1):  # Para cada nivel
    nivel = k  # Número de nivel
    nodo_inicial = 1 + k * (numBayX+1) * (numBayY+1)  # Nodo inicial del nivel
    if nodo_inicial <= total_nodos:  # Si el nodo existe
        coord = ops.nodeCoord(nodo_inicial)  # Obtener coordenadas del nodo
        print(f"Nivel {nivel}: Nodo {nodo_inicial}, Z = {coord[2]} metros")  # Mostrar información

print("\n=== ANÁLISIS ESTRUCTURAL ===")

# Configurar análisis estático
ops.timeSeries('Linear', 1)  # Definir serie de tiempo lineal
ops.pattern('Plain', 1, 1)  # Definir patrón de carga

# Calcular un nodo del último nivel para aplicar la carga
nodo_carga = 1 + numFloor * (numBayX+1) * (numBayY+1)  # Nodo del último nivel
if nodo_carga <= total_nodos:  # Si el nodo existe
    ops.load(nodo_carga, 1, 0, 0, 0, 0, 0)  # Aplicar carga unitaria en dirección X (1 kN)
    print(f"Carga aplicada al nodo {nodo_carga} del último nivel: 1 kN en dirección X")  # Mostrar información de carga
else:  # Si el nodo no existe
    print(f"Error: Nodo {nodo_carga} no existe. Total de nodos: {total_nodos}")  # Mostrar error

ops.analysis('Static')  # Definir tipo de análisis
ops.analyze(10)  # Ejecutar análisis en 10 pasos

print("\n=== VISUALIZACIÓN DEL MODELO ===")

# Configurar parámetros de visualización
az_el    = (-60.0, 30.0)  # Ángulo de vista (azimut, elevación)
fig_wi_he = (20, 15)  # Tamaño de la figura (ancho, alto)

# Intentar visualizar el modelo con configuración detallada
try:  # Intentar visualización detallada
    opsvis.plot_model(  # Función de visualización
        node_labels=0,  # No mostrar etiquetas de nodos
        element_labels=0,  # No mostrar etiquetas de elementos
        offset_nd_label=False,  # Sin offset en etiquetas
        axis_off=0,  # Mostrar ejes
        az_el=az_el,  # Ángulo de vista
        fig_wi_he=fig_wi_he,  # Tamaño de figura
        fig_lbrt=(0.1, 0.1, 0.9, 0.9),  # Márgenes de la figura
        local_axes=False,  # No mostrar ejes locales
        nodes_only=False,  # Mostrar elementos, no solo nodos
        fmt_model={   'color':'blue',  # Color del modelo
                      'linestyle':'solid',  # Estilo de línea
                      'linewidth':1.2,  # Grosor de línea
                      'marker':'',  # Sin marcadores
                      'markersize':6},  # Tamaño de marcadores
        fmt_model_nodes_only={   'color':'blue',  # Color para solo nodos
                                 'linestyle':'solid',  # Estilo de línea
                                 'linewidth':1.2,  # Grosor de línea
                                 'marker':'',  # Sin marcadores
                                 'markersize':6},  # Tamaño de marcadores
        node_supports=True,  # Mostrar apoyos de nodos
        gauss_points=False,  # No mostrar puntos de Gauss
        fmt_gauss_points={   'color':'firebrick',  # Color de puntos Gauss
                             'linestyle':'None',  # Sin línea
                             'linewidth':2.0,  # Grosor de línea
                             'marker':'X',  # Marcador X
                             'markersize':5},  # Tamaño de marcador
        fmt_model_truss={   'color':'green',  # Color para elementos tipo truss
                            'linestyle':'solid',  # Estilo de línea
                            'linewidth':1.2,  # Grosor de línea
                            'marker':'o',  # Marcador circular
                            'markerfacecolor':'white'},  # Color de relleno
        truss_node_offset=0.96,  # Offset para nodos de truss
        ax=False  # No usar eje existente
    )

    plt.title(f"Edificio de {numFloor} plantas - {total_nodos} nodos, {total_elementos} elementos\nSistema Métrico (m, kN, s)")  # Título del gráfico
    plt.show()  # Mostrar gráfico
    print("✓ Visualización completada exitosamente!")  # Mostrar mensaje de éxito
    
except Exception as e:  # Si hay error en la visualización detallada
    print(f"✗ Error en la visualización: {e}")  # Mostrar error
    print("Intentando visualización simple...")  # Mostrar mensaje de intento
    
    try:  # Intentar visualización simple
        opsvis.plot_model()  # Visualización básica
        plt.title(f"Edificio de {numFloor} plantas - Visualización Simple\nSistema Métrico (m, kN, s)")  # Título
        plt.show()  # Mostrar gráfico
        print("✓ Visualización simple completada!")  # Mostrar mensaje de éxito
    except Exception as e2:  # Si también falla la visualización simple
        print(f"✗ Error en visualización simple: {e2}")  # Mostrar error

# Mostrar resumen final del modelo
print(f"\n=== RESUMEN FINAL ===")
print(f"Total de nodos: {total_nodos}")  # Mostrar total de nodos
print(f"Total de elementos: {total_elementos}")  # Mostrar total de elementos
print(f"- Columnas: {total_columnas}")  # Mostrar número de columnas
print(f"- Vigas X: {total_vigas_x}")  # Mostrar número de vigas X
print(f"- Vigas Y: {total_vigas_y}")  # Mostrar número de vigas Y
print(f"Número de plantas: {numFloor}")  # Mostrar número de plantas
print(f"Dimensiones: {numBayX+1} x {numBayY+1} nodos por planta")  # Mostrar dimensiones
print(f"Sistema de unidades: Métrico (m, kN, s)")  # Mostrar sistema de unidades
print(f"Dimensiones totales del edificio:")  # Mostrar título de dimensiones
print(f"  - Ancho X: {sum(bayWidthsX):.2f} metros")  # Mostrar ancho total en X
print(f"  - Ancho Y: {sum(bayWidthsY):.2f} metros")  # Mostrar ancho total en Y
print(f"  - Altura total: {sum(storyHeights):.2f} metros")  # Mostrar altura total
print(f"✓ Vigas conectadas ortogonalmente (no diagonalmente)")  # Mostrar confirmación 