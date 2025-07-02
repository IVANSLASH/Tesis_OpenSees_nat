# Importación de librerías necesarias para el análisis estructural
# pip install openseespy opsvis matplotlib

import openseespy.opensees as ops  # Librería principal de OpenSees para análisis estructural
import opsvis as opsv              # Librería para visualización de modelos OpenSees
import matplotlib.pyplot as plt     # Librería para gráficos y visualización


# ============================================================================
# PARÁMETROS GEOMÉTRICOS Y MATERIALES DE LA LOSA
# ============================================================================

# Parámetros de la losa
L = 5              # Longitud de la losa (en metros) - lado del cuadrado
n = 10             # Número de divisiones por lado (elementos = n x n) - malla de elementos
z = 3.5            # Coordenada Z fija para todos los nodos (altura de la losa)
thickness = 0.2    # Espesor de la losa en metros
E = 100000         # Módulo de elasticidad del material (MPa) - propiedades del material
nu = 0.3           # Coeficiente de Poisson del material


# ============================================================================
# PROPIEDADES DE LA SECCIÓN TRANSVERSAL PARA ELEMENTOS FRAME
# ============================================================================

# Propiedades de la sección transversal para elementos frame (columnas de apoyo)
A = 100                     # Área de la sección transversal (ajusta según sea necesario)
G = E / (2 * (1 + nu))      # Módulo de cortante (relación con E y nu)
J = 1000                    # Constante de torsión (ajusta según sea necesario)
Iy = 1000                   # Momento de inercia en Y (ajusta según sea necesario)
Iz = 1000                   # Momento de inercia en Z (ajusta según sea necesario)

# ============================================================================
# FUNCIÓN PARA GENERAR NODOS DE LA LOSA
# ============================================================================

def generar_nodos(L, n, z):
    """
    Función que genera todos los nodos de la losa en una malla cuadrada
    Parámetros:
    - L: longitud del lado de la losa
    - n: número de divisiones por lado
    - z: altura (coordenada Z) de la losa
    """
    # Limpiar el modelo anterior y crear un nuevo modelo 3D con 6 grados de libertad por nodo
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)

    # Calcular el espaciado entre nodos en X e Y
    dx = L / n  # Espaciado entre nodos en X e Y

    # Generar nodos en una malla cuadrada
    node_tag = 1  # Contador para etiquetas de nodos
    for i in range(n+1):  # Iterar sobre filas (coordenada X)
        x = i * dx  # Calcular coordenada X del nodo
        for j in range(n+1):  # Iterar sobre columnas (coordenada Y)
            y = j * dx  # Calcular coordenada Y del nodo
            # Crear nodo con coordenadas (x, y, z) y etiqueta node_tag
            ops.node(node_tag, x, y, z)
            node_tag += 1  # Incrementar contador de etiquetas

# ============================================================================
# FUNCIÓN PARA GENERAR ELEMENTOS SHELL DE LA LOSA
# ============================================================================

def generar_elementos(n):
    """
    Función que genera todos los elementos ShellMITC4 de la losa
    Parámetros:
    - n: número de divisiones por lado
    """
    # Definir material elástico isótropo para los elementos shell
    ops.nDMaterial('ElasticIsotropic', 1, E, nu)
    # Definir sección de placa con fibras para elementos shell
    ops.section('PlateFiber', 1, 1, thickness)  # (secTag, matTag, thickness)

    # Generar elementos ShellMITC4 en una malla cuadrada
    ele_tag = 1  # Contador para etiquetas de elementos
    for i in range(n):  # Iterar sobre filas de elementos
        for j in range(n):  # Iterar sobre columnas de elementos
            # Calcular etiquetas de los 4 nodos del elemento (en sentido antihorario)
            n1 = i*(n+1) + j + 1      # Nodo inferior izquierdo
            n2 = n1 + 1               # Nodo inferior derecho
            n3 = n1 + (n+1) + 1       # Nodo superior derecho
            n4 = n1 + (n+1)           # Nodo superior izquierdo

            # Crear elemento ShellMITC4 conectando los 4 nodos
            ops.element('ShellMITC4', ele_tag, n1, n2, n3, n4, 1)
            ele_tag += 1  # Incrementar contador de etiquetas

# ============================================================================
# GENERACIÓN DEL MODELO DE LA LOSA
# ============================================================================

# Generar la losa llamando a las funciones definidas
generar_nodos(L, n, z)      # Crear todos los nodos de la losa
generar_elementos(n)        # Crear todos los elementos shell de la losa

# ============================================================================
# CREACIÓN DE NODOS ADICIONALES PARA APOYOS
# ============================================================================

# Definir las etiquetas de los nodos de las esquinas de la losa
esquinas = [1, (n+1), (n*(n+1)+1), (n+1)*(n+1)]  # Esquinas: inf-izq, inf-der, sup-izq, sup-der
q = (n+1)**2  # Calcular el último tag de nodo usado en la losa

# Crear nodos adicionales en el suelo (z=0) para servir como apoyos
ops.node(q+1, 0,   0, 0)  # Nodo de apoyo en esquina inferior izquierda del suelo
ops.node(q+2, 0,   L, 0)  # Nodo de apoyo en esquina inferior derecha del suelo
ops.node(q+3, L,   0, 0)  # Nodo de apoyo en esquina superior izquierda del suelo
ops.node(q+4, L,   L, 0)  # Nodo de apoyo en esquina superior derecha del suelo

# ============================================================================
# APLICACIÓN DE CONDICIONES DE CONTORNO (APOYOS)
# ============================================================================

# Fijar todos los grados de libertad de los nodos de apoyo (1=fijo, 0=libre)
# Formato: fix(nodeTag, ux, uy, uz, rx, ry, rz)
ops.fix(q+1, 1, 1, 1, 1, 1, 1)  # Fijar nodo de apoyo 1 (esquina inf-izq)
ops.fix(q+2, 1, 1, 1, 1, 1, 1)  # Fijar nodo de apoyo 2 (esquina inf-der)
ops.fix(q+3, 1, 1, 1, 1, 1, 1)  # Fijar nodo de apoyo 3 (esquina sup-izq)
ops.fix(q+4, 1, 1, 1, 1, 1, 1)  # Fijar nodo de apoyo 4 (esquina sup-der)

# ============================================================================
# CREACIÓN DE ELEMENTOS FRAME (COLUMNAS DE APOYO)
# ============================================================================

# Crear el material elástico uniaxial para elementos frame
ops.uniaxialMaterial('Elastic', 2, E)               # Usar un tag diferente para evitar conflictos
# Crear transformación geométrica para elementos frame
ops.geomTransf('Linear', 1, *[0, 1, 0])              # Vector y para la transformación geométrica

# Crear los elementos frame que conectan los nodos de apoyo con las esquinas de la losa
for i in range(len(esquinas)):
    # Conectar el nodo de apoyo (q+1, q+2, q+3, q+4) con el nodo de esquina de la losa (esquinas[i])
    ops.element(
        'elasticBeamColumn',           # Tipo de elemento: viga-columna elástica
        q+(i+1), q+(i+1), esquinas[i], # Etiqueta del elemento, nodo inicial, nodo final
        A, E, G, J, Iy, Iz, 1          # Propiedades de la sección y transformación
    )

# ============================================================================
# APLICACIÓN DE CARGAS
# ============================================================================

# Calcular el nodo central de la losa para aplicar la carga
nodo_central = (n//2)*(n+1) + (n//2) + 1
# Definir serie de tiempo lineal para la carga
ops.timeSeries('Linear', 1)
# Definir patrón de carga
ops.pattern('Plain', 1, 1)
# Aplicar carga vertical de -10 kN en el nodo central (negativo = hacia abajo)
ops.load(nodo_central, 0, 0, -10, 0, 0, 0)  # Carga vertical de -10 kN

# ============================================================================
# CONFIGURACIÓN DEL ANÁLISIS ESTÁTICO
# ============================================================================

# Configurar algoritmo de solución no lineal
ops.algorithm('Newton')           # Algoritmo de Newton-Raphson
ops.numberer('RCM')              # Renumeración de ecuaciones (Reverse Cuthill-McKee)
ops.system('ProfileSPD')         # Solucionador de sistema simétrico definido positivo
ops.integrator('LoadControl', 0.1)  # Control de carga con incremento de 0.1
ops.analysis('Static')           # Tipo de análisis: estático
ops.analyze(10)                  # Ejecutar análisis en 10 pasos para mayor desplazamiento acumulado

# ============================================================================
# CONFIGURACIÓN DE LA VISUALIZACIÓN
# ============================================================================

# Parámetros de visualización
az_el = (-60.0, 30.0)           # Ángulo azimut y elevación para la vista 3D
fig_wi_he = (30, 22.5)          # Dimensiones de la figura (ancho, alto)

# ============================================================================
# VISUALIZACIÓN DEL MODELO SIN DEFORMAR
# ============================================================================

# Graficar el modelo estructural sin deformar
opsv.plot_model(
    node_labels=1,               # Mostrar etiquetas de nodos
    element_labels=1,            # Mostrar etiquetas de elementos
    offset_nd_label=False,       # Sin offset en etiquetas de nodos
    axis_off=0,                  # Mostrar ejes de coordenadas
    az_el=az_el,                 # Ángulo de vista
    fig_wi_he=fig_wi_he,         # Tamaño de la figura
    fig_lbrt=(0.1, 0.1, 0.9, 0.9),  # Márgenes de la figura (izq, inf, der, sup)
    local_axes=True,             # Mostrar ejes locales de elementos
    nodes_only=False,            # Mostrar elementos, no solo nodos
    fmt_model={                  # Formato para el modelo
        'color': 'blue', 'linestyle': 'solid',
        'linewidth': 1.2, 'marker': '.', 'markersize': 6
    },
    fmt_model_nodes_only={       # Formato para modelo solo con nodos
        'color': 'blue', 'linestyle': 'solid',
        'linewidth': 1.2, 'marker': '.', 'markersize': 6
    },
    node_supports=True,          # Mostrar apoyos de nodos
    gauss_points=True,           # Mostrar puntos de Gauss
    fmt_gauss_points={           # Formato para puntos de Gauss
        'color': 'firebrick', 'linestyle': 'None',
        'linewidth': 2.0, 'marker': 'X', 'markersize': 5
    },
    fmt_model_truss={            # Formato para elementos tipo truss
        'color': 'green', 'linestyle': 'solid',
        'linewidth': 1.2, 'marker': 'o',
        'markerfacecolor': 'white', 'markersize': 6
    },
    truss_node_offset=0.96,      # Offset para nodos de truss
    ax=False                     # No usar eje existente
)

# ============================================================================
# VISUALIZACIÓN DEL MODELO DEFORMADO
# ============================================================================

# Graficar el modelo estructural deformado
opsv.plot_defo(
    sfac=False,                  # Factor de escala automático
    nep=17,                      # Número de puntos de evaluación por elemento
    unDefoFlag=1,                # Mostrar forma no deformada
    fmt_defo={                   # Formato para forma deformada
        'color': 'blue', 'linestyle': 'solid',
        'linewidth': 1.2, 'marker': '', 'markersize': 1
    },
    fmt_undefo={                 # Formato para forma no deformada
        'color': 'green', 'linestyle': (0, (1, 5)),
        'linewidth': 1.2, 'marker': '.', 'markersize': 1
    },
    fmt_defo_faces={             # Formato para caras deformadas
        'alpha': 0.5, 'edgecolors': 'k', 'linewidths': 1
    },
    fmt_undefo_faces={           # Formato para caras no deformadas
        'alpha': 0.5, 'edgecolors': 'g',
        'facecolors': 'w', 'linestyles': 'dotted', 'linewidths': 1
    },
    interpFlag=1,                # Interpolación activada
    endDispFlag=0,               # No mostrar desplazamientos en extremos
    fmt_nodes={                  # Formato para nodos
        'color': 'red', 'linestyle': 'None',
        'linewidth': 1.2, 'marker': 's', 'markersize': 6
    },
    Eo=0,                        # Desplazamiento inicial
    az_el=az_el,                 # Ángulo de vista
    fig_wi_he=fig_wi_he,         # Tamaño de la figura
    fig_lbrt=(0.1, 0.1, 0.9, 0.9),  # Márgenes de la figura
    node_supports=True,          # Mostrar apoyos de nodos
    ax=False                     # No usar eje existente
)

# ============================================================================
# FINALIZACIÓN DE LA VISUALIZACIÓN
# ============================================================================

# Agregar título a la gráfica
plt.title('Solo la Forma Deformada - Amplificación ', fontsize=4)
# Mostrar la gráfica
plt.show()

# ============================================================================
# FIN DEL SCRIPT
# ============================================================================








