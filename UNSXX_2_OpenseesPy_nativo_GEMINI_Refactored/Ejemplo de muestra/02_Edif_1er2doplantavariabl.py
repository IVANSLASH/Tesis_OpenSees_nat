# Copyright (c) 2023, OpenSeesPy Developers
# All rights reserved.
# Automatiza la creacion de vigas y columnas con alturas personalizables por planta

# Importar librerías necesarias
import opsvis as opsvis  # Librería para visualización de modelos OpenSeesPy
import openseespy.opensees as ops  # Librería principal de OpenSeesPy
import matplotlib.pyplot as plt  # Librería para gráficos
import numpy as np  # Librería para cálculos numéricos
from math import asin  # Función matemática (no se usa en este código)

# Limpiar cualquier modelo anterior y crear uno nuevo
ops.wipe()  # Limpiar el modelo anterior
ops.model('Basic', '-ndm', 3, '-ndf', 6)  # Crear modelo 3D con 6 grados de libertad por nodo

# Definir propiedades geométricas del edificio
numBayX = 2  # Número de vanos en la dirección X
numBayY = 2  # Número de vanos en la dirección Y
numFloor = 4  # Número de pisos
bayWidthX = 120  # Ancho de cada vano en la dirección X (unidades)
bayWidthY = 120  # Ancho de cada vano en la dirección Y (unidades)

# Definir alturas personalizadas por planta
altura_planta_1 = 180  # Altura de la primera planta (puede ser diferente)
altura_planta_2 = 150  # Altura de la segunda planta (puede ser diferente)
altura_plantas_superiores = 162  # Altura para plantas 3 en adelante

# Crear lista de alturas con valores personalizados
storyHeights = []
for i in range(numFloor):
    if i == 0:  # Primera planta
        storyHeights.append(altura_planta_1)
    elif i == 1:  # Segunda planta
        storyHeights.append(altura_planta_2)
    else:  # Plantas superiores
        storyHeights.append(altura_plantas_superiores)

# Propiedades del material
E = 29500  # Módulo de elasticidad del material
massX = 0.49  # Masa en dirección X
M = 0  # Masa adicional para elementos
coordTransf = "Linear"  # Tipo de transformación de coordenadas
massType = "-lMass"  # Tipo de masa (masa distribuida)

print("=== GENERACIÓN DE NODOS ===")
print(f"Alturas por planta: {storyHeights}")

# Inicializar variables para la generación de nodos
nodeTag = 1  # Contador de tags de nodos
zLoc = 0  # Coordenada Z inicial (nivel base)
total_nodos = 0  # Contador total de nodos creados

# Bucle principal para generar todos los nodos del edificio
for k in range(numFloor + 1):  # Para cada nivel (incluyendo base)
    xLoc = 0  # Coordenada X inicial para este nivel
    for i in range(numBayX + 1):  # Para cada nodo en dirección X
        yLoc = 0  # Coordenada Y inicial para esta posición X
        for j in range(numBayY + 1):  # Para cada nodo en dirección Y
            ops.node(nodeTag, xLoc, yLoc, zLoc)  # Crear nodo con coordenadas (x,y,z)
            ops.mass(nodeTag, massX, massX, 0.01, 1.0e-10, 1.0e-10, 1e-10)  # Asignar masa al nodo

            if k == 0:  # Si es el nivel base (k=0)
                ops.fix(nodeTag, 1, 1, 1, 1, 1, 1)  # Empotrar el nodo en todos los grados de libertad

            yLoc += bayWidthY  # Incrementar coordenada Y para el siguiente nodo
            nodeTag += 1  # Incrementar tag del nodo
            total_nodos += 1  # Incrementar contador total

        xLoc += bayWidthX  # Incrementar coordenada X para la siguiente columna

    # Incrementar coordenada Z para el siguiente nivel (excepto para el último nivel)
    if k < numFloor:  # Si no es el último nivel
        storyHeight = storyHeights[k]  # Obtener altura del piso actual
        zLoc += storyHeight  # Incrementar coordenada Z

print(f"Total de nodos creados: {total_nodos}")

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

print(f"Total de columnas creadas: {total_columnas}")

print("=== GENERACIÓN DE VIGAS DIRECCIÓN X ===")

# Inicializar variables para vigas en dirección X
total_vigas_x = 0  # Contador de vigas X
for j in range(1, numFloor + 1):  # Para cada nivel (desde primer piso hasta último)
    nodeTag1 = 1 + j*(numBayX+1)*(numBayY+1)  # Nodo inicial del nivel j (corregido)
    
    for i in range(0, numBayX):  # Para cada vano en dirección X
        for k in range(0, numBayY+1):  # Para cada nodo en dirección Y
            nodeTag2 = nodeTag1 + (numBayX+1)  # Nodo final de la viga (siguiente en X)
            iNode    = ops.nodeCoord(nodeTag1)  # Coordenadas del nodo inicial
            jNode    = ops.nodeCoord(nodeTag2)  # Coordenadas del nodo final
            ops.element(  # Crear elemento viga
                'elasticBeamColumn', eleTag,  # Tipo de elemento
                nodeTag1, nodeTag2,  # Nodos conectados
                50, E, 1000, 1000, 2150, 2150, 2,  # Propiedades: A, E, Iz, Iy, J, G, transfTag
                '-mass', M, massType  # Propiedades de masa
            )
            eleTag   += 1  # Incrementar tag del elemento
            nodeTag1 += 1  # Pasar al siguiente nodo inicial
            total_vigas_x += 1  # Incrementar contador

print(f"Total de vigas en dirección X creadas: {total_vigas_x}")

print("=== GENERACIÓN DE VIGAS DIRECCIÓN Y ===")

# Inicializar variables para vigas en dirección Y
total_vigas_y = 0  # Contador de vigas Y
for j in range(1, numFloor + 1):  # Para cada nivel (desde primer piso hasta último)
    nodeTag1 = 1 + j*(numBayX+1)*(numBayY+1)  # Nodo inicial del nivel j (corregido)
    
    for i in range(0, numBayX+1):  # Para cada nodo en dirección X
        for k in range(0, numBayY):  # Para cada vano en dirección Y
            nodeTag2 = nodeTag1 + 1  # Nodo final de la viga (siguiente en Y)
            iNode    = ops.nodeCoord(nodeTag1)  # Coordenadas del nodo inicial
            jNode    = ops.nodeCoord(nodeTag2)  # Coordenadas del nodo final
            ops.element(  # Crear elemento viga
                'elasticBeamColumn', eleTag,  # Tipo de elemento
                nodeTag1, nodeTag2,  # Nodos conectados
                50, E, 1000, 1000, 2150, 2150, 2,  # Propiedades: A, E, Iz, Iy, J, G, transfTag
                '-mass', M, massType  # Propiedades de masa
            )
            eleTag   += 1  # Incrementar tag del elemento
            nodeTag1 += 1  # Pasar al siguiente nodo inicial
            total_vigas_y += 1  # Incrementar contador
        nodeTag1 += 1  # Saltar al siguiente nodo en X (cambiar de fila)

# Calcular total de elementos
total_elementos = total_columnas + total_vigas_x + total_vigas_y
print(f"Total de elementos creados: {total_elementos}")

# Verificar nodos en diferentes niveles para depuración
print("\n=== VERIFICACIÓN DE NODOS POR NIVEL ===")
for k in range(numFloor + 1):  # Para cada nivel
    nivel = k  # Número de nivel
    nodo_inicial = 1 + k * (numBayX+1) * (numBayY+1)  # Nodo inicial del nivel
    if nodo_inicial <= total_nodos:  # Si el nodo existe
        coord = ops.nodeCoord(nodo_inicial)  # Obtener coordenadas del nodo
        print(f"Nivel {nivel}: Nodo {nodo_inicial}, Z = {coord[2]}")  # Mostrar información

print("\n=== ANÁLISIS ESTRUCTURAL ===")

# Configurar análisis estático
ops.timeSeries('Linear', 1)  # Definir serie de tiempo lineal
ops.pattern('Plain', 1, 1)  # Definir patrón de carga

# Calcular un nodo del último nivel para aplicar la carga
nodo_carga = 1 + numFloor * (numBayX+1) * (numBayY+1)  # Nodo del último nivel
if nodo_carga <= total_nodos:  # Si el nodo existe
    ops.load(nodo_carga, 1, 0, 0, 0, 0, 0)  # Aplicar carga unitaria en dirección X
    print(f"Carga aplicada al nodo {nodo_carga} del último nivel")
else:
    print(f"Error: Nodo {nodo_carga} no existe. Total de nodos: {total_nodos}")

ops.analysis('Static')  # Definir tipo de análisis
ops.analyze(10)  # Ejecutar análisis en 10 pasos

print("\n=== VISUALIZACIÓN DEL MODELO ===")

# Configurar parámetros de visualización
az_el    = (-60.0, 30.0)  # Ángulo de vista (azimut, elevación)
fig_wi_he = (20, 15)  # Tamaño de la figura (ancho, alto)

# Intentar visualizar el modelo con configuración detallada
try:
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

    plt.title(f"Edificio de {numFloor} plantas - {total_nodos} nodos, {total_elementos} elementos")  # Título del gráfico
    plt.show()  # Mostrar gráfico
    print("✓ Visualización completada exitosamente!")
    
except Exception as e:  # Si hay error en la visualización detallada
    print(f"✗ Error en la visualización: {e}")
    print("Intentando visualización simple...")
    
    try:  # Intentar visualización simple
        opsvis.plot_model()  # Visualización básica
        plt.title(f"Edificio de {numFloor} plantas - Visualización Simple")  # Título
        plt.show()  # Mostrar gráfico
        print("✓ Visualización simple completada!")
    except Exception as e2:  # Si también falla la visualización simple
        print(f"✗ Error en visualización simple: {e2}")

# Mostrar resumen final del modelo
print(f"\n=== RESUMEN FINAL ===")
print(f"Total de nodos: {total_nodos}")
print(f"Total de elementos: {total_elementos}")
print(f"- Columnas: {total_columnas}")
print(f"- Vigas X: {total_vigas_x}")
print(f"- Vigas Y: {total_vigas_y}")
print(f"Número de plantas: {numFloor}")
print(f"Dimensiones: {numBayX+1} x {numBayY+1} nodos por planta")
print(f"Alturas por planta: {storyHeights}") 