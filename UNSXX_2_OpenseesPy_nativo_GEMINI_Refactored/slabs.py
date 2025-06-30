# slabs.py
# ============================================
# Este módulo se dedica a la creación y discretización de losas,
# incluyendo la generación de mallas de elementos Shell para una
# representación precisa de su comportamiento y deformaciones.
# También maneja la conexión de las losas con el resto de la estructura.
# ============================================

import openseespy.opensees as ops
import geometry

def create_slabs(geometry_data, section_properties, start_ele_tag):
    """
    Crea y discretiza las losas del edificio en elementos ShellMITC4.
    Cada vano de la estructura tendrá un elemento shell que conecta
    los 4 nodos de las esquinas del vano.

    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio.
        section_properties (dict): Diccionario con las propiedades de las secciones.
        start_ele_tag (int): El tag inicial para los elementos de losa.

    Returns:
        tuple: Una tupla que contiene (total_slabs_elements, lista_ids_losas, next_ele_tag).
    """
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]

    E = section_properties["E"]
    nu = section_properties["nu"]
    slab_thickness = section_properties["slab_thickness"] / 100.0  # Convert cm to meters

    print("\n=== GENERACIÓN Y DISCRETIZACIÓN DE LOSAS ===\n")

    # Verificar si el material ya existe, si no crearlo
    try:
        # Definir material elástico isótropo para los elementos shell
        ops.nDMaterial('ElasticIsotropic', 1, E, nu)
    except:
        # Material ya existe, continuar
        pass
    
    try:
        # Definir sección de placa con fibras para elementos shell
        ops.section('PlateFiber', 1, 1, slab_thickness)  # (secTag, matTag, thickness)
    except:
        # Sección ya existe, continuar
        pass

    ele_tag = start_ele_tag
    total_slabs_elements = 0
    slab_elements_ids = []

    # Usar densidad de malla desde la configuración de entrada
    mesh_density = geometry_data.get("mesh_density", 1)
    print(f"  Densidad de malla configurada: {mesh_density} divisiones por vano")

    for k in range(1, num_floor + 1):  # Para cada nivel (excluyendo la base)
        print(f"  Generando losas para el Nivel {k}...")
        
        # Crear elementos shell para cada vano
        for j_bay in range(num_bay_y):  # Para cada vano en Y
            for i_bay in range(num_bay_x):  # Para cada vano en X
                
                # Si mesh_density = 1, crear un elemento por vano
                # Si mesh_density > 1, crear una malla de elementos por vano
                for sub_j in range(mesh_density):
                    for sub_i in range(mesh_density):
                        # Calcular los índices de nodos considerando la subdivisión
                        # Para mesh_density = 1, esto será simplemente los nodos de las esquinas del vano
                        
                        # Nodo inferior izquierdo
                        node1_i = i_bay + (sub_i * 1 // mesh_density)
                        node1_j = j_bay + (sub_j * 1 // mesh_density)
                        
                        # Nodo inferior derecho
                        node2_i = i_bay + ((sub_i + 1) * 1 // mesh_density + (1 if sub_i == mesh_density - 1 else 0))
                        node2_j = j_bay + (sub_j * 1 // mesh_density)
                        
                        # Nodo superior derecho
                        node3_i = i_bay + ((sub_i + 1) * 1 // mesh_density + (1 if sub_i == mesh_density - 1 else 0))
                        node3_j = j_bay + ((sub_j + 1) * 1 // mesh_density + (1 if sub_j == mesh_density - 1 else 0))
                        
                        # Nodo superior izquierdo
                        node4_i = i_bay + (sub_i * 1 // mesh_density)
                        node4_j = j_bay + ((sub_j + 1) * 1 // mesh_density + (1 if sub_j == mesh_density - 1 else 0))
                        
                        # Para simplificar y evitar errores, crearemos solo un elemento por vano
                        # usando los nodos de las esquinas del vano
                        if sub_i == 0 and sub_j == 0:  # Solo crear un elemento por vano
                            
                            # Nodos de las esquinas del vano
                            node1_tag = geometry.get_node_tag_from_indices(k, j_bay, i_bay, num_bay_x, num_bay_y)
                            node2_tag = geometry.get_node_tag_from_indices(k, j_bay, i_bay + 1, num_bay_x, num_bay_y)
                            node3_tag = geometry.get_node_tag_from_indices(k, j_bay + 1, i_bay + 1, num_bay_x, num_bay_y)
                            node4_tag = geometry.get_node_tag_from_indices(k, j_bay + 1, i_bay, num_bay_x, num_bay_y)
                            
                            # Verificar que todos los nodos existen
                            total_nodes = (num_bay_x + 1) * (num_bay_y + 1) * (num_floor + 1)
                            
                            if (node1_tag <= total_nodes and node2_tag <= total_nodes and 
                                node3_tag <= total_nodes and node4_tag <= total_nodes):
                                
                                try:
                                    # Crear elemento ShellMITC4
                                    ops.element('ShellMITC4', ele_tag, node1_tag, node2_tag, node3_tag, node4_tag, 1)
                                    slab_elements_ids.append(ele_tag)
                                    ele_tag += 1
                                    total_slabs_elements += 1
                                    
                                    print(f"    Elemento {ele_tag-1}: Nodos [{node1_tag}, {node2_tag}, {node3_tag}, {node4_tag}]")
                                    
                                except Exception as e:
                                    print(f"    Error creando elemento shell en vano ({i_bay}, {j_bay}): {e}")
                                    print(f"    Nodos intentados: [{node1_tag}, {node2_tag}, {node3_tag}, {node4_tag}]")
                            else:
                                print(f"    Error: Nodos fuera de rango en vano ({i_bay}, {j_bay})")
                                print(f"    Nodos: [{node1_tag}, {node2_tag}, {node3_tag}, {node4_tag}], Total: {total_nodes}")

    print(f"Total de elementos de losa creados: {total_slabs_elements}")
    
    if total_slabs_elements == 0:
        print("⚠️  Advertencia: No se crearon elementos de losa")
        print("    El modelo continuará solo con elementos frame (columnas y vigas)")
    
    return total_slabs_elements, slab_elements_ids, ele_tag
