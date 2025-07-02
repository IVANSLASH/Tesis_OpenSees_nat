# Importación de librerías necesarias para el análisis estructural
# pip install openseespy opsvis matplotlib

import openseespy.opensees as ops  # Librería principal de OpenSees para análisis estructural
import opsvis as opsv              # Librería para visualización de modelos OpenSees
import matplotlib.pyplot as plt     # Librería para gráficos y visualización
import numpy as np                  # Librería para operaciones numéricas


# ============================================================================
# CONFIGURACIÓN DE PARÁMETROS GEOMÉTRICOS Y MATERIALES
# ============================================================================

def obtener_configuracion_usuario():
    """
    Función para obtener la configuración del usuario
    """
    print("=" * 60)
    print("    SISTEMA AUTOMATIZADO DE MÚLTIPLES LOSAS")
    print("=" * 60)
    # Valores predeterminados sugeridos
    num_vanos_x = 2
    num_vanos_y = 2
    largo_vano_x = 4.0
    largo_vano_y = 4.0
    divisiones_por_vano = 10
    altura_losa = 4.0
    espesor_losa = 0.4
    E = 1000.0
    nu = 0.3
    print(f"Usando valores predeterminados:\n  Vanos X: {num_vanos_x}, Vanos Y: {num_vanos_y}, Lx: {largo_vano_x}, Ly: {largo_vano_y}, Divisiones: {divisiones_por_vano}, Altura: {altura_losa}, Espesor: {espesor_losa}, E: {E}, nu: {nu}")
    return {
        'num_vanos_x': num_vanos_x,
        'num_vanos_y': num_vanos_y,
        'largo_vano_x': largo_vano_x,
        'largo_vano_y': largo_vano_y,
        'divisiones_por_vano': divisiones_por_vano,
        'altura_losa': altura_losa,
        'espesor_losa': espesor_losa,
        'E': E,
        'nu': nu
    }

# ============================================================================
# FUNCIÓN PARA GENERAR NODOS DE MÚLTIPLES LOSAS
# ============================================================================

def generar_nodos_multiplos_losas(config):
    """
    Función que genera todos los nodos para múltiples losas
    """
    # Limpiar modelo anterior
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)
    
    # Extraer parámetros
    nx = config['num_vanos_x']
    ny = config['num_vanos_y']
    lx = config['largo_vano_x']
    ly = config['largo_vano_y']
    n_div = config['divisiones_por_vano']
    z = config['altura_losa']
    
    # Calcular dimensiones totales
    Lx_total = nx * lx
    Ly_total = ny * ly
    
    # Calcular espaciado
    dx = lx / n_div
    dy = ly / n_div
    
    # Calcular número total de nodos por nivel
    num_nodos_x = nx * n_div + 1
    num_nodos_y = ny * n_div + 1
    
    print(f"\n📊 GENERANDO NODOS:")
    print(f"   Dimensiones totales: {Lx_total:.2f}m x {Ly_total:.2f}m")
    print(f"   Nodos por nivel: {num_nodos_x} x {num_nodos_y} = {num_nodos_x * num_nodos_y}")
    
    # Generar nodos en malla rectangular
    node_tag = 1
    for i in range(num_nodos_x):
        x = i * dx
        for j in range(num_nodos_y):
            y = j * dy
            ops.node(node_tag, x, y, z)
            node_tag += 1
    
    return num_nodos_x, num_nodos_y, node_tag - 1

# ============================================================================
# FUNCIÓN PARA GENERAR ELEMENTOS SHELL DE MÚLTIPLES LOSAS
# ============================================================================

def generar_elementos_multiplos_losas(config, num_nodos_x, num_nodos_y):
    """
    Función que genera todos los elementos ShellMITC4 para múltiples losas
    """
    # Definir material y sección
    E = config['E']
    nu = config['nu']
    thickness = config['espesor_losa']
    
    ops.nDMaterial('ElasticIsotropic', 1, E, nu)
    ops.section('PlateFiber', 1, 1, thickness)
    
    # Generar elementos ShellMITC4
    ele_tag = 1
    for i in range(num_nodos_x - 1):
        for j in range(num_nodos_y - 1):
            # Calcular etiquetas de los 4 nodos del elemento
            n1 = i * num_nodos_y + j + 1
            n2 = n1 + 1
            n3 = n1 + num_nodos_y + 1
            n4 = n1 + num_nodos_y
            
            # Crear elemento ShellMITC4
            ops.element('ShellMITC4', ele_tag, n1, n2, n3, n4, 1)
            ele_tag += 1
    
    print(f"   Elementos de losa creados: {ele_tag - 1}")
    return ele_tag - 1

# ============================================================================
# FUNCIÓN PARA CREAR APOYOS EN CADA INTERSECCIÓN DE VANOS
# ============================================================================

def crear_apoyos_intersecciones(config, num_nodos_x, num_nodos_y, ultimo_nodo_losa):
    """
    Función para crear nodos de apoyo en cada intersección de vanos
    """
    nx = config['num_vanos_x']
    ny = config['num_vanos_y']
    n_div = config['divisiones_por_vano']
    
    # Calcular posiciones de columnas (cada n_div nodos)
    posiciones_x = [i * n_div for i in range(nx + 1)]
    posiciones_y = [j * n_div for j in range(ny + 1)]
    
    # Crear nodos de apoyo en cada intersección
    nodos_apoyo = []
    esquinas_losa = []
    nodo_apoyo_tag = ultimo_nodo_losa + 1
    
    for i, pos_x in enumerate(posiciones_x):
        for j, pos_y in enumerate(posiciones_y):
            # Calcular nodo de la losa correspondiente
            nodo_losa = pos_x * num_nodos_y + pos_y + 1
            
            # Obtener coordenadas del nodo de la losa
            coord = ops.nodeCoord(nodo_losa)
            x, y = coord[0], coord[1]
            
            # Crear nodo de apoyo
            ops.node(nodo_apoyo_tag, x, y, 0)
            nodos_apoyo.append(nodo_apoyo_tag)
            esquinas_losa.append(nodo_losa)
            
            # Fijar todos los grados de libertad
            ops.fix(nodo_apoyo_tag, 1, 1, 1, 1, 1, 1)
            
            nodo_apoyo_tag += 1
    
    print(f"   Nodos de apoyo creados: {len(nodos_apoyo)} (en cada intersección de vanos)")
    return nodos_apoyo, esquinas_losa

# ============================================================================
# FUNCIÓN PARA CREAR COLUMNAS DE APOYO
# ============================================================================

def crear_columnas_apoyo(nodos_apoyo, esquinas_losa, config):
    """
    Función para crear elementos frame que conectan apoyos con esquinas de la losa
    """
    E = config['E']
    nu = config['nu']
    G = E / (2 * (1 + nu))
    
    # Propiedades de sección para columnas
    A = 100
    J = 1000
    Iy = 1000
    Iz = 1000
    
    # Crear material y transformación
    ops.uniaxialMaterial('Elastic', 2, E)
    ops.geomTransf('Linear', 1, *[0, 1, 0])
    
    # Crear elementos frame
    ele_tag_columna = 1000  # Empezar con tag diferente
    for i, (apoyo, esquina) in enumerate(zip(nodos_apoyo, esquinas_losa)):
        ops.element(
            'elasticBeamColumn',
            ele_tag_columna + i,
            apoyo, esquina,
            A, E, G, J, Iy, Iz, 1
        )
    
    print(f"   Columnas de apoyo creadas: {len(nodos_apoyo)}")
    return len(nodos_apoyo)

# ============================================================================
# FUNCIÓN PARA CREAR VIGAS EN DIRECCIÓN X
# ============================================================================

def crear_vigas_direccion_x(config, esquinas_losa):
    """
    Función para crear vigas en dirección X conectando columnas
    """
    nx = config['num_vanos_x']
    ny = config['num_vanos_y']
    E = config['E']
    nu = config['nu']
    G = E / (2 * (1 + nu))
    A = 80
    J = 800
    Iy = 800
    Iz = 800
    ops.uniaxialMaterial('Elastic', 3, E)
    ops.geomTransf('Linear', 2, *[0, 0, 1])
    ele_tag_viga = 2000
    num_vigas_x = 0
    
    # Crear vigas en dirección X entre columnas
    for fila in range(ny + 1):  # Para cada fila de columnas
        for col in range(nx):    # Para cada vano en X
            # Calcular índices de columnas conectadas
            idx_col1 = fila * (nx + 1) + col
            idx_col2 = fila * (nx + 1) + col + 1
            
            # Crear viga conectando las dos columnas
            ops.element(
                'elasticBeamColumn',
                ele_tag_viga + num_vigas_x,
                esquinas_losa[idx_col1], esquinas_losa[idx_col2],
                A, E, G, J, Iy, Iz, 2
            )
            num_vigas_x += 1
    
    print(f"   Vigas en dirección X creadas: {num_vigas_x}")
    return num_vigas_x

# ============================================================================
# FUNCIÓN PARA CREAR VIGAS EN DIRECCIÓN Y
# ============================================================================

def crear_vigas_direccion_y(config, esquinas_losa):
    """
    Función para crear vigas en dirección Y conectando columnas
    """
    nx = config['num_vanos_x']
    ny = config['num_vanos_y']
    E = config['E']
    nu = config['nu']
    G = E / (2 * (1 + nu))
    A = 80
    J = 800
    Iy = 800
    Iz = 800
    ops.uniaxialMaterial('Elastic', 4, E)
    ops.geomTransf('Linear', 3, *[0, 0, 1])
    ele_tag_viga = 3000
    num_vigas_y = 0
    
    # Crear vigas en dirección Y entre columnas
    for col in range(nx + 1):  # Para cada columna de columnas
        for fila in range(ny):  # Para cada vano en Y
            # Calcular índices de columnas conectadas
            idx_col1 = fila * (nx + 1) + col
            idx_col2 = (fila + 1) * (nx + 1) + col
            
            # Crear viga conectando las dos columnas
            ops.element(
                'elasticBeamColumn',
                ele_tag_viga + num_vigas_y,
                esquinas_losa[idx_col1], esquinas_losa[idx_col2],
                A, E, G, J, Iy, Iz, 3
            )
            num_vigas_y += 1
    
    print(f"   Vigas en dirección Y creadas: {num_vigas_y}")
    return num_vigas_y

# ============================================================================
# FUNCIÓN PARA APLICAR CARGAS DISTRIBUIDAS
# ============================================================================

def aplicar_cargas_distribuidas(num_nodos_x, num_nodos_y, config):
    """
    Función para aplicar cargas distribuidas en todos los nodos
    """
    # Definir serie de tiempo y patrón de carga
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    
    # Carga distribuida por nodo (kN)
    carga_por_nodo = float(input("\n💪 Carga distribuida por nodo (kN): ") or "1.0")
    
    # Aplicar carga a todos los nodos de la losa
    for i in range(1, num_nodos_x * num_nodos_y + 1):
        ops.load(i, 0, 0, -carga_por_nodo, 0, 0, 0)
    
    print(f"   Carga aplicada a {num_nodos_x * num_nodos_y} nodos")
    return carga_por_nodo

# ============================================================================
# FUNCIÓN PARA CONFIGURAR Y EJECUTAR ANÁLISIS
# ============================================================================

def ejecutar_analisis():
    """
    Función para configurar y ejecutar el análisis estático
    """
    print("\n🔬 CONFIGURANDO ANÁLISIS...")
    
    # Configurar algoritmo de solución
    ops.algorithm('Newton')
    ops.numberer('RCM')
    ops.system('ProfileSPD')
    ops.integrator('LoadControl', 0.1)
    ops.analysis('Static')
    
    # Ejecutar análisis
    print("   Ejecutando análisis estático...")
    ops.analyze(10)
    print("   ✅ Análisis completado exitosamente")

# ============================================================================
# FUNCIÓN PARA VISUALIZACIÓN
# ============================================================================

def generar_visualizaciones():
    """
    Función para generar todas las visualizaciones
    """
    print("\n🎨 GENERANDO VISUALIZACIONES...")
    
    # Parámetros de visualización
    az_el = (-60.0, 30.0)
    fig_wi_he = (30, 22.5)
    
    # 1. Modelo sin deformar
    print("   1️⃣ Generando modelo sin deformar...")
    opsv.plot_model(
        node_labels=1,
        element_labels=1,
        offset_nd_label=False,
        axis_off=0,
        az_el=az_el,
        fig_wi_he=fig_wi_he,
        fig_lbrt=(0.1, 0.1, 0.9, 0.9),
        local_axes=True,
        nodes_only=False,
        fmt_model={
            'color': 'blue', 'linestyle': 'solid',
            'linewidth': 1.2, 'marker': '.', 'markersize': 6
        },
        node_supports=True,
        gauss_points=True,
        fmt_gauss_points={
            'color': 'firebrick', 'linestyle': 'None',
            'linewidth': 2.0, 'marker': 'X', 'markersize': 5
        },
        ax=False
    )
    
    # 2. Modelo deformado
    print("   2️⃣ Generando modelo deformado...")
    opsv.plot_defo(
        sfac=False,
        nep=17,
        unDefoFlag=1,
        fmt_defo={
            'color': 'blue', 'linestyle': 'solid',
            'linewidth': 1.2, 'marker': '', 'markersize': 1
        },
        fmt_undefo={
            'color': 'green', 'linestyle': (0, (1, 5)),
            'linewidth': 1.2, 'marker': '.', 'markersize': 1
        },
        fmt_defo_faces={
            'alpha': 0.5, 'edgecolors': 'k', 'linewidths': 1
        },
        fmt_undefo_faces={
            'alpha': 0.5, 'edgecolors': 'g',
            'facecolors': 'w', 'linestyles': 'dotted', 'linewidths': 1
        },
        interpFlag=1,
        endDispFlag=0,
        fmt_nodes={
            'color': 'red', 'linestyle': 'None',
            'linewidth': 1.2, 'marker': 's', 'markersize': 6
        },
        Eo=0,
        az_el=az_el,
        fig_wi_he=fig_wi_he,
        fig_lbrt=(0.1, 0.1, 0.9, 0.9),
        node_supports=True,
        ax=False
    )
    
    # Agregar título y mostrar
    plt.title('Sistema de Múltiples Losas - Deformación', fontsize=14)
    plt.show()

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que orquesta todo el proceso
    """
    try:
        print("🚀 INICIANDO SISTEMA AUTOMATIZADO DE MÚLTIPLES LOSAS")
        
        # 1. Obtener configuración del usuario
        config = obtener_configuracion_usuario()
        
        # 2. Generar nodos
        num_nodos_x, num_nodos_y, ultimo_nodo = generar_nodos_multiplos_losas(config)
        
        # 3. Generar elementos de losa
        num_elementos_losa = generar_elementos_multiplos_losas(config, num_nodos_x, num_nodos_y)
        
        # 4. Crear apoyos
        nodos_apoyo, esquinas_losa = crear_apoyos_intersecciones(config, num_nodos_x, num_nodos_y, ultimo_nodo)
        
        # 5. Crear columnas de apoyo
        num_columnas = crear_columnas_apoyo(nodos_apoyo, esquinas_losa, config)
        
        # 6. Crear vigas en dirección X
        num_vigas_x = crear_vigas_direccion_x(config, esquinas_losa)
        
        # 7. Crear vigas en dirección Y
        num_vigas_y = crear_vigas_direccion_y(config, esquinas_losa)
        
        # 8. Aplicar cargas
        carga_aplicada = aplicar_cargas_distribuidas(num_nodos_x, num_nodos_y, config)
        
        # 9. Ejecutar análisis
        ejecutar_analisis()
        
        # 10. Generar visualizaciones
        generar_visualizaciones()
        
        # 11. Resumen final
        print("\n" + "=" * 60)
        print("🎉 ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 RESUMEN DEL MODELO:")
        print(f"   • Vanos: {config['num_vanos_x']} x {config['num_vanos_y']}")
        print(f"   • Dimensiones: {config['num_vanos_x'] * config['largo_vano_x']:.2f}m x {config['num_vanos_y'] * config['largo_vano_y']:.2f}m")
        print(f"   • Nodos: {num_nodos_x * num_nodos_y}")
        print(f"   • Elementos de losa: {num_elementos_losa}")
        print(f"   • Columnas de apoyo: {num_columnas}")
        print(f"   • Vigas en dirección X: {num_vigas_x}")
        print(f"   • Vigas en dirección Y: {num_vigas_y}")
        print(f"   • Carga aplicada: {carga_aplicada} kN/nodo")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("💡 Verifique los parámetros de entrada")

# ============================================================================
# EJECUCIÓN DEL PROGRAMA
# ============================================================================

if __name__ == "__main__":
    main()








