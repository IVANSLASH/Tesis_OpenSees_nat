# geometry.py
# ============================================
# Este módulo se encarga de la definición de la geometría estructural:
# creación de nodos, elementos (columnas y vigas) y la asignación de
# sus propiedades geométricas y de conectividad. Se enfoca en la
# construcción del esqueleto del edificio.
# ============================================

import openseespy.opensees as ops
import numpy as np

def get_node_tag_from_indices(floor_idx, bay_y_idx, bay_x_idx, num_bay_x, num_bay_y):
    """
    Calcula el tag del nodo basándose en sus índices de piso, vano en Y y vano en X.
    Asume que los nodos se crean secuencialmente como en create_nodes.

    Args:
        floor_idx (int): Índice del piso (0 para la base).
        bay_y_idx (int): Índice de la posición en Y (0 a num_bay_y).
        bay_x_idx (int): Índice de la posición en X (0 a num_bay_x).
        num_bay_x (int): Número total de vanos en dirección X.
        num_bay_y (int): Número total de vanos en dirección Y.

    Returns:
        int: El tag del nodo correspondiente.
    """
    nodes_per_level = (num_bay_x + 1) * (num_bay_y + 1)
    node_tag = 1 + floor_idx * nodes_per_level + bay_y_idx * (num_bay_x + 1) + bay_x_idx
    return node_tag

def create_nodes(geometry_data, E, massX, M, massType):
    """
    Crea los nodos del modelo OpenSeesPy basándose en los datos de geometría.
    
    Esta función genera todos los nodos de la estructura en un patrón 3D regular,
    desde la base (nivel 0) hasta el último nivel, incluyendo las masas
    correspondientes y las restricciones en la base.

    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio.
        E (float): Módulo de elasticidad del material (no usado aquí, para compatibilidad).
        massX (float): Masa en dirección X para los nodos (toneladas).
        M (float): Masa adicional para elementos (no usado aquí, para compatibilidad).
        massType (str): Tipo de masa para los elementos (no usado aquí, para compatibilidad).

    Returns:
        int: El número total de nodos creados en la estructura.
    """
    # Extraer datos de geometría del diccionario de entrada
    num_bay_x = geometry_data["num_bay_x"]          # Número de vanos en dirección X
    num_bay_y = geometry_data["num_bay_y"]          # Número de vanos en dirección Y  
    num_floor = geometry_data["num_floor"]          # Número de pisos del edificio
    bay_widths_x = geometry_data["bay_widths_x"]    # Lista con anchos de vanos en X (metros)
    bay_widths_y = geometry_data["bay_widths_y"]    # Lista con anchos de vanos en Y (metros)
    story_heights = geometry_data["story_heights"]  # Lista con alturas de pisos (metros)

    print("\n=== GENERACIÓN DE NODOS ===\n")

    node_tag = 1        # Contador de tags de nodos (empieza en 1)
    total_nodos = 0     # Contador del total de nodos creados

    # Generar nodos para cada nivel del edificio (incluyendo la base)
    for k in range(num_floor + 1):  # k = nivel (0=base, 1=primer piso, etc.)
        z_loc = 0       # Coordenada Z del nivel actual
        
        # Calcular altura acumulada hasta el nivel actual
        if k > 0:
            for piso in range(k):
                z_loc += story_heights[piso]    # Sumar alturas de pisos anteriores

        # Generar nodos en cada fila Y del nivel actual
        for j in range(num_bay_y + 1):      # j = posición en Y (0 a num_bay_y)
            y_loc = 0   # Coordenada Y de la fila actual
            
            # Calcular distancia acumulada en Y hasta la posición actual
            if j > 0:
                for vano in range(j):
                    y_loc += bay_widths_y[vano]    # Sumar anchos de vanos anteriores en Y

            # Generar nodos en cada columna X de la fila actual
            for i in range(num_bay_x + 1):  # i = posición en X (0 a num_bay_x)
                x_loc = 0   # Coordenada X de la columna actual
                
                # Calcular distancia acumulada en X hasta la posición actual
                if i > 0:
                    for vano in range(i):
                        x_loc += bay_widths_x[vano]    # Sumar anchos de vanos anteriores en X

                # Crear el nodo con las coordenadas calculadas
                ops.node(node_tag, x_loc, y_loc, z_loc)
                
                # Asignar masa al nodo (para análisis dinámico)
                # massX en X e Y, masa pequeña en Z, momentos de inercia pequeños
                ops.mass(node_tag, massX, massX, 0.01, 1.0e-10, 1.0e-10, 1e-10)

                # Si estamos en la base (k=0), aplicar restricciones de empotramiento
                if k == 0:  
                    ops.fix(node_tag, 1, 1, 1, 1, 1, 1)    # Restringir todos los 6 grados de libertad

                node_tag += 1       # Incrementar tag para el siguiente nodo
                total_nodos += 1    # Incrementar contador total

    print(f"Total de nodos creados: {total_nodos}")

    nodos_por_nivel = (num_bay_x + 1) * (num_bay_y + 1)
    total_nodos_esperados = (num_floor + 1) * nodos_por_nivel
    print(f"\n=== VERIFICACIÓN DE NODOS ===\n")
    print(f"Nodos por nivel: {nodos_por_nivel}")
    print(f"Total de niveles: {num_floor + 1}")
    print(f"Total de nodos esperados: {total_nodos_esperados}")
    print(f"Total de nodos creados: {total_nodos}")
    if total_nodos != total_nodos_esperados:
        print(f"⚠️  ADVERTENCIA: Diferencia en número de nodos!")

    print("\n=== DEPURACIÓN: NUMERACIÓN DE NODOS ===\n")
    for k in range(num_floor + 1):
        print(f"\nNivel {k}:")
        nodo_inicial = 1 + k * nodos_por_nivel
        print(f"  Nodo inicial del nivel: {nodo_inicial}")
        for j in range(num_bay_y + 1):
            fila = []
            for i in range(num_bay_x + 1):
                node_tag_current = nodo_inicial + j * (num_bay_x + 1) + i
                if node_tag_current <= total_nodos:
                    coord = ops.nodeCoord(node_tag_current)
                    fila.append(f"N{node_tag_current}({coord[0]:.1f},{coord[1]:.1f},{coord[2]:.1f})")
                else:
                    fila.append(f"N{node_tag_current}(NO_EXISTE)")
            print(f"  Fila {j}: {' | '.join(fila)}")
    return total_nodos

def create_columns(geometry_data, E, M, massType, A_col, Iz_col, Iy_col, J_col):
    """
    Crea los elementos columna del modelo OpenSeesPy.

    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio.
        E (float): Módulo de elasticidad del material.
        M (float): Masa adicional para elementos.
        massType (str): Tipo de masa para los elementos.
        A_col (float): Área de la sección de la columna.
        Iz_col (float): Momento de inercia Iz de la columna.
        Iy_col (float): Momento de inercia Iy de la columna.
        J_col (float): Constante de torsión J de la columna.

    Returns:
        tuple: Una tupla que contiene (total_columnas, lista_ids_columnas, next_ele_tag).
    """
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]

    print("\n=== GENERACIÓN DE COLUMNAS ===\n")

    ele_tag = 1  # Se asume que los elementos empiezan desde 1
    node_tag_base = 1
    total_columnas = 0
    column_elements_ids = []
    nodos_por_nivel = (num_bay_x + 1) * (num_bay_y + 1)

    ops.geomTransf("Linear", 1, 1, 0, 0)  # Transformación para columnas (eje Y)

    for k in range(0, num_floor):
        for i in range(0, num_bay_x + 1):
            for j in range(0, num_bay_y + 1):
                node_tag1 = node_tag_base + k * nodos_por_nivel + j * (num_bay_x + 1) + i
                node_tag2 = node_tag1 + nodos_por_nivel

                ops.element(
                    'elasticBeamColumn', ele_tag,
                    node_tag1, node_tag2,
                    A_col, E, Iz_col, Iy_col, J_col, E, 1, # A, E, Iz, Iy, J, G, transfTag
                    '-mass', M, massType
                )
                column_elements_ids.append(ele_tag)
                ele_tag += 1
                total_columnas += 1

    print(f"Total de columnas creadas: {total_columnas}")
    return total_columnas, column_elements_ids, ele_tag

def create_beams(geometry_data, E, M, massType, A_viga, Iz_viga, Iy_viga, J_viga, start_ele_tag, total_nodes):
    """
    Crea los elementos viga del modelo OpenSeesPy.
    SOLO genera vigas ortogonales en el mismo nivel.

    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio.
        E (float): Módulo de elasticidad del material.
        M (float): Masa adicional para elementos.
        massType (str): Tipo de masa para los elementos.
        A_viga (float): Área de la sección de la viga.
        Iz_viga (float): Momento de inercia Iz de la viga.
        Iy_viga (float): Momento de inercia Iy de la viga.
        J_viga (float): Constante de torsión J de la viga.
        start_ele_tag (int): El tag inicial para los elementos viga.
        total_nodes (int): El número total de nodos en el modelo.

    Returns:
        tuple: Una tupla que contiene (total_vigas_x, lista_ids_vigas_x, total_vigas_y, lista_ids_vigas_y, next_ele_tag).
    """
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]

    ele_tag = start_ele_tag
    total_vigas_x = 0
    beam_elements_x_ids = []
    total_vigas_y = 0
    beam_elements_y_ids = []
    nodos_por_nivel = (num_bay_x + 1) * (num_bay_y + 1)

    ops.geomTransf("Linear", 2, 0, 0, 1)  # Transformación para vigas (eje Z)

    print("\n=== GENERACIÓN DE VIGAS DIRECCIÓN X (ORTOGONALES) ===\n")
    for k in range(1, num_floor + 1):
        nodo_inicial_nivel = 1 + k * nodos_por_nivel
        for j in range(num_bay_y + 1):
            nodo_inicial_fila = nodo_inicial_nivel + j * (num_bay_x + 1)
            for i in range(num_bay_x):
                node_tag1 = nodo_inicial_fila + i
                node_tag2 = node_tag1 + 1
                if node_tag1 <= total_nodes and node_tag2 <= total_nodes:
                    coord1 = ops.nodeCoord(node_tag1)
                    coord2 = ops.nodeCoord(node_tag2)
                    # Verificar que los nodos están en la misma línea Y y Z (ortogonal)
                    if abs(coord1[1] - coord2[1]) < 0.001 and abs(coord1[2] - coord2[2]) < 0.001:
                        ops.element(
                            'elasticBeamColumn', ele_tag,
                            node_tag1, node_tag2,
                            A_viga, E, Iz_viga, Iy_viga, J_viga, E, 2, # A, E, Iz, Iy, J, G, transfTag
                            '-mass', M, massType
                        )
                        beam_elements_x_ids.append(ele_tag)
                        ele_tag += 1
                        total_vigas_x += 1
                    else:
                        print(f"      ⚠️ Saltando viga diagonal: nodos {node_tag1} y {node_tag2} no están en la misma línea Y")
                else:
                    print(f"      ERROR: Nodos {node_tag1} o {node_tag2} no existen (total: {total_nodes})")
    print(f"Total de vigas en dirección X creadas: {total_vigas_x}")

    print("\n=== GENERACIÓN DE VIGAS DIRECCIÓN Y (ORTOGONALES) ===\n")
    for k in range(1, num_floor + 1):
        nodo_inicial_nivel = 1 + k * nodos_por_nivel
        for i in range(num_bay_x + 1):
            for j in range(num_bay_y):
                node_tag1 = nodo_inicial_nivel + j * (num_bay_x + 1) + i
                node_tag2 = node_tag1 + (num_bay_x + 1)
                if node_tag1 <= total_nodes and node_tag2 <= total_nodes:
                    coord1 = ops.nodeCoord(node_tag1)
                    coord2 = ops.nodeCoord(node_tag2)
                    # Verificar que los nodos están en la misma línea X y Z (ortogonal)
                    if abs(coord1[0] - coord2[0]) < 0.001 and abs(coord1[2] - coord2[2]) < 0.001:
                        ops.element(
                            'elasticBeamColumn', ele_tag,
                            node_tag1, node_tag2,
                            A_viga, E, Iz_viga, Iy_viga, J_viga, E, 2, # A, E, Iz, Iy, J, G, transfTag
                            '-mass', M, massType
                        )
                        beam_elements_y_ids.append(ele_tag)
                        ele_tag += 1
                        total_vigas_y += 1
                    else:
                        print(f"      ⚠️ Saltando viga diagonal: nodos {node_tag1} y {node_tag2} no están en la misma línea X")
                else:
                    print(f"      ERROR: Nodos {node_tag1} o {node_tag2} no existen (total: {total_nodes})")
    print(f"Total de vigas en dirección Y creadas: {total_vigas_y}")
    print(f"✅ TODAS las vigas son ortogonales y están en el mismo nivel")

    return total_vigas_x, beam_elements_x_ids, total_vigas_y, beam_elements_y_ids, ele_tag