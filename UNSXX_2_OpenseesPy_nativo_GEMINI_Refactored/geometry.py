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

    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio.
        E (float): Módulo de elasticidad del material.
        massX (float): Masa en dirección X para los nodos.
        M (float): Masa adicional para elementos.
        massType (str): Tipo de masa para los elementos.

    Returns:
        int: El número total de nodos creados.
    """
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]
    bay_widths_x = geometry_data["bay_widths_x"]
    bay_widths_y = geometry_data["bay_widths_y"]
    story_heights = geometry_data["story_heights"]

    print("\n=== GENERACIÓN DE NODOS ===\n")

    node_tag = 1
    total_nodos = 0

    for k in range(num_floor + 1):  # Para cada nivel (incluyendo base)
        z_loc = 0
        if k > 0:
            for piso in range(k):
                z_loc += story_heights[piso]

        for j in range(num_bay_y + 1):
            y_loc = 0
            if j > 0:
                for vano in range(j):
                    y_loc += bay_widths_y[vano]

            for i in range(num_bay_x + 1):
                x_loc = 0
                if i > 0:
                    for vano in range(i):
                        x_loc += bay_widths_x[vano]

                ops.node(node_tag, x_loc, y_loc, z_loc)
                ops.mass(node_tag, massX, massX, 0.01, 1.0e-10, 1.0e-10, 1e-10)

                if k == 0:  # Si es el nivel base (k=0)
                    ops.fix(node_tag, 1, 1, 1, 1, 1, 1)

                node_tag += 1
                total_nodos += 1

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

    print("\n=== GENERACIÓN DE VIGAS DIRECCIÓN X ===\n")
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
                    if abs(coord1[1] - coord2[1]) < 0.001:
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
                        print(f"      ERROR: Nodos {node_tag1} y {node_tag2} no están en la misma fila Y")
                else:
                    print(f"      ERROR: Nodos {node_tag1} o {node_tag2} no existen (total: {total_nodes})")
    print(f"Total de vigas en dirección X creadas: {total_vigas_x}")

    print("\n=== GENERACIÓN DE VIGAS DIRECCIÓN Y ===\n")
    for k in range(1, num_floor + 1):
        nodo_inicial_nivel = 1 + k * nodos_por_nivel
        for i in range(num_bay_x + 1):
            for j in range(num_bay_y):
                node_tag1 = nodo_inicial_nivel + j * (num_bay_x + 1) + i
                node_tag2 = node_tag1 + (num_bay_x + 1)
                if node_tag1 <= total_nodes and node_tag2 <= total_nodes:
                    coord1 = ops.nodeCoord(node_tag1)
                    coord2 = ops.nodeCoord(node_tag2)
                    if abs(coord1[0] - coord2[0]) < 0.001:
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
                        print(f"      ERROR: Nodos {node_tag1} y {node_tag2} no están en la misma columna X")
                else:
                    print(f"      ERROR: Nodos {node_tag1} o {node_tag2} no existen (total: {total_nodes})")
    print(f"Total de vigas en dirección Y creadas: {total_vigas_y}")

    return total_vigas_x, beam_elements_x_ids, total_vigas_y, beam_elements_y_ids, ele_tag