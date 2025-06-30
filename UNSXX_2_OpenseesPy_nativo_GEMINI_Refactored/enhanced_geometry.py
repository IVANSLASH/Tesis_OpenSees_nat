# enhanced_geometry.py
# ============================================
# Módulo para generación de geometría mejorada que incluye:
# - Secciones de columnas personalizadas
# - Volados (cantilevers) frontales y laterales
# - Vigas de borde para volados
# - Actualización de nodos y elementos
# ============================================

import openseespy.opensees as ops
import numpy as np

def generate_enhanced_nodes(geometry_data, cantilever_config):
    """
    Genera nodos incluyendo los volados configurados.
    """
    bay_widths_x = geometry_data["bay_widths_x"]
    bay_widths_y = geometry_data["bay_widths_y"]
    story_heights = geometry_data["story_heights"]
    num_floor = geometry_data["num_floor"]
    
    # Calcular coordenadas base de la estructura original
    x_coords = [0]
    for width in bay_widths_x:
        x_coords.append(x_coords[-1] + width)
    
    y_coords = [0]
    for width in bay_widths_y:
        y_coords.append(y_coords[-1] + width)
    
    z_coords = [0]
    for height in story_heights:
        z_coords.append(z_coords[-1] + height)
    
    # Calcular coordenadas extendidas incluyendo volados
    extended_x_coords = x_coords.copy()
    extended_y_coords = y_coords.copy()
    
    # Agregar coordenadas de volados
    if cantilever_config['front']:
        # Volado frontal: agregar coordenada X adicional
        front_length = cantilever_config['front']['length']
        extended_x_coords.append(x_coords[-1] + front_length)
    
    if cantilever_config['right']:
        # Volado derecho: agregar coordenada Y adicional (positiva)
        right_length = cantilever_config['right']['length']
        extended_y_coords.append(y_coords[-1] + right_length)
    
    if cantilever_config['left']:
        # Volado izquierdo: agregar coordenada Y adicional (negativa)
        left_length = cantilever_config['left']['length']
        extended_y_coords.insert(0, y_coords[0] - left_length)
    
    # Generar nodos
    node_id = 1
    node_mapping = {}  # Para mapear (x_idx, y_idx, z_idx) -> node_id
    
    print(f"  Generando nodos para estructura con volados...")
    print(f"    Coordenadas X: {len(extended_x_coords)} posiciones")
    print(f"    Coordenadas Y: {len(extended_y_coords)} posiciones")
    print(f"    Coordenadas Z: {len(z_coords)} posiciones")
    
    for k, z in enumerate(z_coords):
        for i, x in enumerate(extended_x_coords):
            for j, y in enumerate(extended_y_coords):
                
                # Determinar si este nodo debe existir en este nivel
                should_create_node = True
                
                if k == 0:
                    # Nivel 0: Solo nodos de la estructura original
                    if (i >= len(x_coords) or j >= len(y_coords) or 
                        (cantilever_config['left'] and j == 0)):
                        should_create_node = False
                        
                elif k == 1:
                    # Nivel 1: Estructura original + INICIO de volados para estabilidad
                    # Ajustar índices para volado izquierdo
                    effective_j = j - (1 if cantilever_config['left'] else 0)
                    
                    if (cantilever_config['left'] and j == 0):
                        # Nodo de volado izquierdo (desde nivel 1)
                        should_create_node = i < len(x_coords)
                    elif (cantilever_config['front'] and i == len(extended_x_coords) - 1):
                        # Nodo de volado frontal (desde nivel 1)
                        should_create_node = effective_j < len(y_coords)
                    elif (cantilever_config['right'] and j == len(extended_y_coords) - 1):
                        # Nodo de volado derecho (desde nivel 1)
                        should_create_node = i < len(x_coords)
                    else:
                        # Nodos de estructura original
                        should_create_node = (i < len(x_coords) and effective_j < len(y_coords))
                        
                else:
                    # Niveles 2+: Estructura original + volados
                    # Ajustar índices para volado izquierdo
                    effective_j = j - (1 if cantilever_config['left'] else 0)
                    
                    if (cantilever_config['left'] and j == 0):
                        # Nodo de volado izquierdo
                        should_create_node = i < len(x_coords)
                    elif (cantilever_config['front'] and i == len(extended_x_coords) - 1):
                        # Nodo de volado frontal
                        should_create_node = effective_j < len(y_coords)
                    elif (cantilever_config['right'] and j == len(extended_y_coords) - 1):
                        # Nodo de volado derecho
                        should_create_node = i < len(x_coords)
                    else:
                        # Nodos de estructura original
                        should_create_node = (i < len(x_coords) and effective_j < len(y_coords))
                
                if should_create_node:
                    ops.node(node_id, x, y, z)
                    node_mapping[(i, j, k)] = node_id
                    node_id += 1
    
    total_nodes = node_id - 1
    print(f"    ✅ {total_nodes} nodos generados exitosamente")
    
    # Debug: Mostrar algunos nodos de volados para verificar
    if any(cantilever_config.values()):
        print(f"\n    🔍 VERIFICACIÓN DE NODOS DE VOLADOS:")
        node_tags = list(range(1, min(node_id, 21)))  # Primeros 20 nodos
        for tag in node_tags:
            try:
                coord = ops.nodeCoord(tag)
                print(f"      Nodo {tag}: ({coord[0]:.2f}, {coord[1]:.2f}, {coord[2]:.2f})")
            except:
                pass
        
        # Mostrar coordenadas extendidas
        print(f"    📏 COORDENADAS EXTENDIDAS:")
        print(f"      X: {extended_x_coords}")
        print(f"      Y: {extended_y_coords}")
    
    return total_nodes, node_mapping, extended_x_coords, extended_y_coords, z_coords

def generate_enhanced_column_elements(node_mapping, geometry_data, column_config, 
                                    extended_x_coords, extended_y_coords, z_coords):
    """
    Genera elementos de columna con secciones personalizadas.
    """
    story_heights = geometry_data["story_heights"]
    num_floor = geometry_data["num_floor"]
    material_data = geometry_data.get("material_data", {})
    
    # Obtener coordenadas de estructura original
    bay_widths_x = geometry_data["bay_widths_x"]
    bay_widths_y = geometry_data["bay_widths_y"]
    original_x_count = len(bay_widths_x) + 1
    original_y_count = len(bay_widths_y) + 1
    
    column_elements_ids = []
    element_id = 1
    
    print(f"  Generando columnas con configuración: {column_config['type']}")
    
    # Crear transformaciones de coordenadas PRIMERO (verificar si no existen)
    print("    Creando transformaciones de coordenadas...")
    try:
        ops.geomTransf('Linear', 1, 1, 0, 0)  # Para columnas (dirección Z)
        print("      ✅ Transformación 1 (columnas) creada")
    except:
        print("      ⚠️ Transformación 1 ya existe")
    
    try:
        ops.geomTransf('Linear', 2, 0, 0, 1)  # Para vigas X (dirección Y)
        print("      ✅ Transformación 2 (vigas X) creada")
    except:
        print("      ⚠️ Transformación 2 ya existe")
    
    try:
        ops.geomTransf('Linear', 3, 0, 0, 1)  # Para vigas Y (dirección X)
        print("      ✅ Transformación 3 (vigas Y) creada")
    except:
        print("      ⚠️ Transformación 3 ya existe")
    
    # Crear materiales para diferentes tipos de columnas
    if column_config['type'] == 'uniform':
        create_column_material(1, column_config)
        
    elif column_config['type'] == 'exterior_interior':
        create_column_material(1, column_config['exterior'])  # Exteriores
        create_column_material(2, column_config['interior'])  # Interiores
        
    elif column_config['type'] == 'custom_groups':
        for group_id, group_data in column_config['groups'].items():
            create_column_material(group_id, group_data)
    
    # Generar elementos de columna
    for k in range(len(z_coords) - 1):  # Para cada nivel
        for i in range(original_x_count):  # Solo estructura original
            for j in range(original_y_count):
                
                # Ajustar índices para volado izquierdo
                j_adjusted = j + (1 if 'left' in [key for key, val in geometry_data.get('cantilever_config', {}).items() if val] else 0)
                
                # Verificar que ambos nodos existen
                node_bottom = node_mapping.get((i, j_adjusted, k))
                node_top = node_mapping.get((i, j_adjusted, k + 1))
                
                if node_bottom and node_top:
                    # Determinar material y sección según configuración
                    if column_config['type'] == 'uniform':
                        material_id = 1
                        
                    elif column_config['type'] == 'exterior_interior':
                        # Determinar si es exterior o interior
                        is_exterior = (i == 0 or i == original_x_count - 1 or 
                                     j == 0 or j == original_y_count - 1)
                        material_id = 1 if is_exterior else 2
                        
                    elif column_config['type'] == 'custom_groups':
                        # Calcular ID del grupo
                        group_id = i * original_y_count + j + 1
                        material_id = group_id
                    
                    # Crear elemento
                    ops.element('elasticBeamColumn', element_id, node_bottom, node_top,
                              material_id, geometry_data.get("transf_tag_col", 1))
                    
                    column_elements_ids.append(element_id)
                    element_id += 1
    
    print(f"    ✅ {len(column_elements_ids)} elementos de columna generados")
    return column_elements_ids, element_id

def generate_enhanced_beam_elements(node_mapping, geometry_data, cantilever_config,
                                  extended_x_coords, extended_y_coords, z_coords, start_element_id):
    """
    Genera elementos de viga incluyendo vigas de borde para volados.
    """
    bay_widths_x = geometry_data["bay_widths_x"]
    bay_widths_y = geometry_data["bay_widths_y"]
    original_x_count = len(bay_widths_x) + 1
    original_y_count = len(bay_widths_y) + 1
    
    beam_elements_x_ids = []
    beam_elements_y_ids = []
    cantilever_beam_ids = []
    element_id = start_element_id
    
    print(f"  Generando vigas principales y de volados...")
    
    # Crear material para vigas principales (usar sección del geometry_data)
    section_properties = geometry_data.get('section_properties', {})
    beam_section_tag = 2  # Tag por defecto
    
    if section_properties:
        # Verificar si la sección 2 ya existe y usar tag diferente si es necesario
        try:
            # Intentar crear la sección con tag 2
            ops.section('Elastic', 2, 25000000.0, 
                       section_properties.get('A_viga', 0.15), 
                       section_properties.get('Iz_viga', 0.0028125),
                       section_properties.get('Iy_viga', 0.0005), 
                       25000000.0/2.4, 
                       section_properties.get('J_viga', 0.0033125))
            print("    ✅ Sección de vigas principales creada con tag 2")
            beam_section_tag = 2
        except:
            # Si falla, usar tag 20 para vigas principales en enhanced_geometry
            print("    ⚠️ Sección tag 2 ya existe, usando tag 20 para vigas principales")
            ops.section('Elastic', 20, 25000000.0, 
                       section_properties.get('A_viga', 0.15), 
                       section_properties.get('Iz_viga', 0.0028125),
                       section_properties.get('Iy_viga', 0.0005), 
                       25000000.0/2.4, 
                       section_properties.get('J_viga', 0.0033125))
            beam_section_tag = 20
    
    # Crear materiales para vigas de volado si es necesario
    if cantilever_config['front']:
        create_cantilever_beam_material(101, cantilever_config['front']['edge_beam'])
    if cantilever_config['right']:
        create_cantilever_beam_material(102, cantilever_config['right']['edge_beam'])
    if cantilever_config['left']:
        create_cantilever_beam_material(103, cantilever_config['left']['edge_beam'])
    
    # Generar vigas para cada nivel (empezando desde nivel 1)
    for k in range(1, len(z_coords)):
        level = k  # Nivel actual (1, 2, 3, ...)
        
        # Ajuste para volado izquierdo
        y_offset = 1 if cantilever_config['left'] else 0
        
        # VIGAS EN DIRECCIÓN X (entre columnas de la estructura original)
        for i in range(original_x_count - 1):  # Entre columnas en X
            for j in range(original_y_count):  # En cada línea Y
                
                j_adjusted = j + y_offset
                
                node1 = node_mapping.get((i, j_adjusted, k))
                node2 = node_mapping.get((i + 1, j_adjusted, k))
                
                if node1 and node2:
                    ops.element('elasticBeamColumn', element_id, node1, node2,
                              beam_section_tag, 2)  # sección beam_section_tag, transformación 2
                    beam_elements_x_ids.append(element_id)
                    element_id += 1
        
        # VIGAS EN DIRECCIÓN Y (entre columnas de la estructura original)
        for i in range(original_x_count):  # En cada línea X
            for j in range(original_y_count - 1):  # Entre columnas en Y
                
                j_adjusted = j + y_offset
                
                node1 = node_mapping.get((i, j_adjusted, k))
                node2 = node_mapping.get((i, j_adjusted + 1, k))
                
                if node1 and node2:
                    ops.element('elasticBeamColumn', element_id, node1, node2,
                              beam_section_tag, 3)  # sección beam_section_tag, transformación 3
                    beam_elements_y_ids.append(element_id)
                    element_id += 1
        
        # VIGAS DE VOLADOS (desde nivel 1 para estabilidad)
        if level >= 1:
            
            # Volado frontal
            if cantilever_config['front']:
                front_x_idx = len(extended_x_coords) - 1
                for j in range(original_y_count):
                    j_adjusted = j + y_offset
                    
                    # Viga desde último nodo estructura a nodo volado
                    node1 = node_mapping.get((original_x_count - 1, j_adjusted, k))
                    node2 = node_mapping.get((front_x_idx, j_adjusted, k))
                    
                    if node1 and node2:
                        ops.element('elasticBeamColumn', element_id, node1, node2,
                                  101, 2)  # sección 101, transformación 2
                        cantilever_beam_ids.append(element_id)
                        element_id += 1
                
                # Viga de borde frontal (conecta nodos del volado frontal)
                for j in range(original_y_count - 1):
                    j_adjusted = j + y_offset
                    
                    node1 = node_mapping.get((front_x_idx, j_adjusted, k))
                    node2 = node_mapping.get((front_x_idx, j_adjusted + 1, k))
                    
                    if node1 and node2:
                        ops.element('elasticBeamColumn', element_id, node1, node2,
                                  101, 3)  # sección 101, transformación 3
                        cantilever_beam_ids.append(element_id)
                        element_id += 1
            
            # Volado lateral derecho
            if cantilever_config['right']:
                right_y_idx = len(extended_y_coords) - 1
                for i in range(original_x_count):
                    
                    # Viga desde último nodo estructura a nodo volado
                    node1 = node_mapping.get((i, original_y_count - 1 + y_offset, k))
                    node2 = node_mapping.get((i, right_y_idx, k))
                    
                    if node1 and node2:
                        ops.element('elasticBeamColumn', element_id, node1, node2,
                                  102, 3)  # sección 102, transformación 3
                        cantilever_beam_ids.append(element_id)
                        element_id += 1
                
                # Viga de borde derecha
                for i in range(original_x_count - 1):
                    node1 = node_mapping.get((i, right_y_idx, k))
                    node2 = node_mapping.get((i + 1, right_y_idx, k))
                    
                    if node1 and node2:
                        ops.element('elasticBeamColumn', element_id, node1, node2,
                                  102, 2)  # sección 102, transformación 2
                        cantilever_beam_ids.append(element_id)
                        element_id += 1
            
            # Volado lateral izquierdo
            if cantilever_config['left']:
                left_y_idx = 0
                for i in range(original_x_count):
                    
                    # Viga desde primer nodo estructura a nodo volado
                    node1 = node_mapping.get((i, y_offset, k))
                    node2 = node_mapping.get((i, left_y_idx, k))
                    
                    if node1 and node2:
                        ops.element('elasticBeamColumn', element_id, node1, node2,
                                  103, 3)  # sección 103, transformación 3
                        cantilever_beam_ids.append(element_id)
                        element_id += 1
                
                # Viga de borde izquierda
                for i in range(original_x_count - 1):
                    node1 = node_mapping.get((i, left_y_idx, k))
                    node2 = node_mapping.get((i + 1, left_y_idx, k))
                    
                    if node1 and node2:
                        ops.element('elasticBeamColumn', element_id, node1, node2,
                                  103, 2)  # sección 103, transformación 2
                        cantilever_beam_ids.append(element_id)
                        element_id += 1
    
    print(f"    ✅ {len(beam_elements_x_ids)} vigas en X, {len(beam_elements_y_ids)} vigas en Y")
    print(f"    ✅ {len(cantilever_beam_ids)} vigas de volado generadas")
    
    # Debug: Mostrar información de elementos de volado
    if cantilever_beam_ids:
        print(f"\n    🔍 VERIFICACIÓN DE ELEMENTOS DE VOLADO:")
        for i, elem_id in enumerate(cantilever_beam_ids[:5]):  # Primeros 5 elementos
            try:
                nodes = ops.eleNodes(elem_id)
                coord1 = ops.nodeCoord(nodes[0])
                coord2 = ops.nodeCoord(nodes[1])
                print(f"      Elemento {elem_id}: Nodos {nodes[0]}-{nodes[1]}")
                print(f"        Nodo {nodes[0]}: ({coord1[0]:.2f}, {coord1[1]:.2f}, {coord1[2]:.2f})")
                print(f"        Nodo {nodes[1]}: ({coord2[0]:.2f}, {coord2[1]:.2f}, {coord2[2]:.2f})")
            except Exception as e:
                print(f"      Error verificando elemento {elem_id}: {e}")
    
    return beam_elements_x_ids, beam_elements_y_ids, cantilever_beam_ids, element_id

def create_column_material(material_id, column_data):
    """
    Crea material y sección para columna.
    """
    E = 25000000.0  # kN/m² (25 GPa)
    G = E / 2.4      # Módulo de corte
    A = column_data['A_col']
    Iz = column_data['Iz_col']
    Iy = column_data['Iy_col']
    J = Iz + Iy  # Momento polar aproximado
    
    try:
        ops.section('Elastic', material_id, E, A, Iz, Iy, G, J)
        print(f"      ✅ Sección de columna {material_id} creada")
    except:
        print(f"      ⚠️ Sección de columna {material_id} ya existe")

def create_cantilever_beam_material(material_id, beam_data):
    """
    Crea material y sección para viga de volado.
    """
    E = 25000000.0  # kN/m² (25 GPa)
    G = E / 2.4      # Módulo de corte
    A = beam_data['A']
    Iz = beam_data['Iz']
    Iy = beam_data['Iy']
    J = Iz + Iy  # Momento polar aproximado
    
    try:
        ops.section('Elastic', material_id, E, A, Iz, Iy, G, J)
        print(f"      ✅ Sección de viga de volado {material_id} creada")
    except:
        print(f"      ⚠️ Sección de viga de volado {material_id} ya existe")

def apply_enhanced_boundary_conditions(node_mapping, extended_x_coords, extended_y_coords, cantilever_config):
    """
    Aplica condiciones de frontera considerando la geometría con volados.
    """
    print("  Aplicando condiciones de frontera...")
    
    # Obtener dimensiones de estructura original
    original_x_count = len(extended_x_coords)
    original_y_count = len(extended_y_coords)
    
    # Ajustar si hay volado frontal
    if cantilever_config['front']:
        original_x_count -= 1
    
    # Ajustar si hay volados laterales
    if cantilever_config['right']:
        original_y_count -= 1
    if cantilever_config['left']:
        original_y_count -= 1
        
    # Aplicar restricciones en la base (nivel 0)
    restricted_nodes = 0
    y_offset = 1 if cantilever_config['left'] else 0
    
    for i in range(original_x_count):
        for j in range(original_y_count):
            j_adjusted = j + y_offset
            node_id = node_mapping.get((i, j_adjusted, 0))
            
            if node_id:
                ops.fix(node_id, 1, 1, 1, 1, 1, 1)  # Empotramiento completo
                restricted_nodes += 1
    
    print(f"    ✅ {restricted_nodes} nodos restringidos en la base")
    
    # Debug: Verificar algunos nodos restringidos
    if restricted_nodes > 0:
        print(f"    🔍 VERIFICACIÓN DE RESTRICCIONES:")
        restricted_count = 0
        for i in range(min(original_x_count, 3)):  # Solo primeros 3 para debug
            for j in range(min(original_y_count, 3)):
                j_adjusted = j + y_offset
                node_id = node_mapping.get((i, j_adjusted, 0))
                if node_id:
                    coord = ops.nodeCoord(node_id)
                    print(f"      Nodo {node_id}: ({coord[0]:.2f}, {coord[1]:.2f}, {coord[2]:.2f}) - EMPOTRADO")
                    restricted_count += 1
                    if restricted_count >= 6:  # Máximo 6 para debug
                        break
            if restricted_count >= 6:
                break
    else:
        print("    ❌ ADVERTENCIA: No se aplicaron restricciones")
    
    return restricted_nodes