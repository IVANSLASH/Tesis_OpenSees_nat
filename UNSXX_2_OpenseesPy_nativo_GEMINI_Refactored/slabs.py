# slabs.py
# ============================================
# Este módulo se dedica a la creación y discretización de losas,
# implementando un sistema de mallado para una representación precisa.
# ============================================

import openseespy.opensees as ops
import numpy as np

def create_slab_mesh(p1, p2, p3, p4, nx, ny, sec_tag, start_ele_tag, start_node_tag):
    """
    Crea una malla de elementos ShellMITC4 para un solo paño de losa.

    Args:
        p1, p2, p3, p4: Coordenadas de las 4 esquinas del paño de losa.
        nx, ny: Número de divisiones de la malla en cada dirección (e.g., 10x10).
        sec_tag: Tag de la sección a utilizar para los elementos de losa.
        start_ele_tag: Tag inicial para los nuevos elementos.
        start_node_tag: Tag inicial para los nuevos nodos internos.

    Returns:
        tuple: (lista_ids_elementos, siguiente_ele_tag, siguiente_node_tag)
    """
    ele_tag = start_ele_tag
    node_tag = start_node_tag
    slab_elements_ids = []
    
    # Generar una matriz de nodos para la malla
    nodes_grid = np.full((ny + 1, nx + 1), 0, dtype=int)

    for j in range(ny + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            # Interpolar coordenadas para encontrar la posición del nodo
            coord_jv = (1 - v) * p1 + v * p4
            coord_iv = (1 - v) * p2 + v * p3
            coord = (1 - u) * coord_jv + u * coord_iv
            
            # Reutilizar nodos existentes en los bordes
            # Esta es una simplificación. Para un caso real, se necesitaría un mapa de nodos global.
            # Por ahora, creamos nuevos nodos para toda la malla para robustez.
            ops.node(node_tag, *coord)
            nodes_grid[j, i] = node_tag
            node_tag += 1

    # Crear elementos Shell conectando los nodos de la malla
    for j in range(ny):
        for i in range(nx):
            n1 = nodes_grid[j, i]
            n2 = nodes_grid[j, i + 1]
            n3 = nodes_grid[j + 1, i + 1]
            n4 = nodes_grid[j + 1, i]
            ops.element('ShellMITC4', ele_tag, n1, n2, n3, n4, sec_tag)
            slab_elements_ids.append(ele_tag)
            ele_tag += 1
            
    return slab_elements_ids, ele_tag, node_tag

def create_slabs(geometry_data, section_properties, start_ele_tag):
    """
    Crea y discretiza las losas del edificio con una malla de 10x10 por vano.
    """
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]
    span_x = geometry_data["span_x"]
    span_y = geometry_data["span_y"]
    story_height = geometry_data["story_height"]

    E = section_properties["E"]
    nu = section_properties["nu"]
    slab_thickness = section_properties["slab_thickness"] / 100.0

    print("\n=== GENERACIÓN Y DISCRETIZACIÓN DE LOSAS (MALLA 10x10) ===\n")

    sec_tag = 1 # Asumimos que la sección de la losa tiene tag 1
    try:
        ops.nDMaterial('ElasticIsotropic', sec_tag, E, nu)
        ops.section('PlateFiber', sec_tag, sec_tag, slab_thickness)
    except Exception as e:
        print(f"Nota: Material/Sección de losa ya podría existir. {e}")

    ele_tag = start_ele_tag
    # Empezar a numerar los nodos de la malla desde un número alto para evitar colisiones
    node_tag = (num_bay_x + 1) * (num_bay_y + 1) * (num_floor + 1) + 1000 
    total_slabs_elements = []

    nx, ny = 10, 10 # Malla de 10x10
    print(f"  Configurando malla de {nx}x{ny} para cada paño de losa.")

    for k in range(1, num_floor + 1):
        z = k * story_height
        print(f"  Generando losas para el Nivel {k} (Z = {z:.2f}m)...")
        for j_bay in range(num_bay_y):
            for i_bay in range(num_bay_x):
                # Definir las 4 esquinas del paño de losa actual
                p1 = np.array([i_bay * span_x, j_bay * span_y, z])
                p2 = np.array([(i_bay + 1) * span_x, j_bay * span_y, z])
                p3 = np.array([(i_bay + 1) * span_x, (j_bay + 1) * span_y, z])
                p4 = np.array([i_bay * span_x, (j_bay + 1) * span_y, z])
                
                # Crear la malla para este paño
                slab_ids, ele_tag, node_tag = create_slab_mesh(p1, p2, p3, p4, nx, ny, sec_tag, ele_tag, node_tag)
                total_slabs_elements.extend(slab_ids)
                print(f"    Paño ({i_bay}, {j_bay}): Creados {len(slab_ids)} elementos de losa.")

    print(f"\nTotal de elementos de losa creados: {len(total_slabs_elements)}")
    if not total_slabs_elements:
        print("⚠️ Advertencia: No se crearon elementos de losa.")
    
    return len(total_slabs_elements), total_slabs_elements, ele_tag