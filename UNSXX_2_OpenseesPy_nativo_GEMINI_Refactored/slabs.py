# slabs.py
# ============================================
# Este módulo se dedica a la creación y discretización de losas,
# implementando un sistema de mallado robusto para una representación precisa.
# ============================================

import openseespy.opensees as ops
import numpy as np
import geometry # Importar para la función de obtener nodos

def create_slabs(geometry_data, section_properties, start_ele_tag):
    """
    Crea elementos de losa simplificados para evitar corrupción de memoria.
    Usa elementos shell básicos sin malla compleja.
    """
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]

    E = section_properties["E"]
    nu = section_properties["nu"]
    slab_thickness = section_properties["slab_thickness"] / 100.0

    print("\n=== GENERACIÓN SIMPLIFICADA DE LOSAS ===")

    # Crear material y sección para losas
    slab_mat_tag = 101
    slab_sec_tag = 101
    try:
        ops.nDMaterial('ElasticIsotropic', slab_mat_tag, E, nu)
        ops.section('PlateFiber', slab_sec_tag, slab_mat_tag, slab_thickness)
        print(f"    ✅ Material y sección de losa creados (Tag {slab_sec_tag})")
    except Exception as e:
        print(f"    ⚠️ Material/Sección de losa ya existe: {e}")

    ele_tag = start_ele_tag
    total_slab_elements = []

    print(f"  Creando elementos de losa básicos para {num_floor} niveles...")

    for k in range(1, num_floor + 1):  # Para cada nivel
        print(f"    Nivel {k}:")
        for j_bay in range(num_bay_y):
            for i_bay in range(num_bay_x):
                # Obtener los tags de los 4 nodos de esquina del paño actual
                try:
                    n1_tag = geometry.get_node_tag_from_indices(k, j_bay, i_bay, num_bay_x, num_bay_y)
                    n2_tag = geometry.get_node_tag_from_indices(k, j_bay, i_bay + 1, num_bay_x, num_bay_y)
                    n3_tag = geometry.get_node_tag_from_indices(k, j_bay + 1, i_bay + 1, num_bay_x, num_bay_y)
                    n4_tag = geometry.get_node_tag_from_indices(k, j_bay + 1, i_bay, num_bay_x, num_bay_y)

                    # Crear elemento shell simple
                    ops.element('ShellMITC4', ele_tag, n1_tag, n2_tag, n3_tag, n4_tag, slab_sec_tag)
                    total_slab_elements.append(ele_tag)
                    ele_tag += 1
                    
                except Exception as e:
                    print(f"      ❌ Error en paño ({i_bay}, {j_bay}): {e}")
                    continue

    print(f"\nTotal de elementos de losa creados: {len(total_slab_elements)}")
    if not total_slab_elements:
        print("⚠️ Advertencia: No se crearon elementos de losa.")
    
    return len(total_slab_elements), total_slab_elements, ele_tag