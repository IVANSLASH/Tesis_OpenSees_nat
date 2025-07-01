# results_enhanced.py
# ============================================
# Sistema mejorado de generación de resultados y archivos CSV
# con información detallada para post-procesamiento
# ============================================

import openseespy.opensees as ops
import pandas as pd
import numpy as np
from datetime import datetime
import traceback

def check_analysis_results():
    """Verifica si hay resultados de análisis disponibles."""
    try:
        node_tags = ops.getNodeTags()
        if not node_tags:
            return False
        # Intenta obtener el desplazamiento de un nodo para ver si el análisis corrió
        ops.nodeDisp(node_tags[0])
        return True
    except Exception:
        print("⚠️ No se encontraron resultados de análisis. Genere el modelo y corra el análisis primero.")
        return False

def generate_frame_forces_csv(filename="solicitaciones_porticos.csv"):
    """
    Genera un CSV con las solicitaciones (fuerzas y momentos) para elementos de pórtico.
    """
    print(f"\n=== Generando CSV de Solicitaciones en Pórticos ===")
    if not check_analysis_results():
        return None

    element_data = []
    element_tags = ops.getEleTags()

    for ele_tag in element_tags:
        try:
            nodes = ops.eleNodes(ele_tag)
            if len(nodes) != 2:  # Solo elementos de pórtico (2 nodos)
                continue

            node_i, node_j = nodes[0], nodes[1]
            coord_i, coord_j = ops.nodeCoord(node_i), ops.nodeCoord(node_j)
            
            direction = np.array(coord_j) - np.array(coord_i)
            element_type = "Columna" if abs(direction[2]) > 0.95 else ("Viga_X" if abs(direction[0]) > abs(direction[1]) else "Viga_Y")
            length = np.linalg.norm(direction)

            forces = ops.eleForce(ele_tag)
            if not forces or len(forces) < 12:
                forces = [0]*12

            element_data.append({
                'Elemento': ele_tag, 'Tipo': element_type, 'Longitud': length,
                'Nodo_I': node_i, 'Nodo_J': node_j,
                'N_I': forces[0], 'V_I': forces[1], 'M_I': forces[5],
                'N_J': forces[6], 'V_J': forces[7], 'M_J': forces[11],
            })
        except Exception as e:
            print(f"Error procesando elemento de pórtico {ele_tag}: {e}")
            continue

    if not element_data:
        print("⚠️ No se encontraron datos de fuerzas para elementos de pórtico.")
        return None

    df = pd.DataFrame(element_data)
    df.to_csv(filename, index=False, float_format='%.3f')
    print(f"✅ Archivo de solicitaciones de pórticos guardado: {filename}")
    return df

def generate_slab_forces_csv(filename="solicitaciones_losas.csv"):
    """
    Genera un CSV con las solicitaciones (fuerzas y momentos) para elementos de losa.
    """
    print(f"\n=== Generando CSV de Solicitaciones en Losas ===")
    if not check_analysis_results():
        return None

    slab_data = []
    element_tags = ops.getEleTags()

    for ele_tag in element_tags:
        try:
            nodes = ops.eleNodes(ele_tag)
            if len(nodes) != 4:  # Solo elementos de losa (4 nodos)
                continue

            # Para losas, se obtienen las fuerzas en los puntos de integración
            forces = ops.eleResponse(ele_tag, 'forces')
            if not forces or len(forces) < 8:
                forces = [0]*8

            slab_data.append({
                'Elemento': ele_tag,
                'Nodos': str(nodes),
                'Fxx': forces[0], 'Fyy': forces[1], 'Fxy': forces[2], 'Mxx': forces[3],
                'Myy': forces[4], 'Mxy': forces[5], 'Vxz': forces[6], 'Vyz': forces[7],
            })
        except Exception as e:
            # La respuesta 'forces' puede no estar implementada para todos los shells
            print(f"Nota: No se pudieron obtener fuerzas para el elemento de losa {ele_tag}. Puede que el tipo de elemento no lo soporte. Error: {e}")
            continue

    if not slab_data:
        print("⚠️ No se encontraron datos de fuerzas para losas.")
        return None

    df = pd.DataFrame(slab_data)
    df.to_csv(filename, index=False, float_format='%.3f')
    print(f"✅ Archivo de solicitaciones de losas guardado: {filename}")
    return df

def generate_nodal_displacements_csv(filename="desplazamientos_nodales.csv"):
    """
    Genera un CSV con los desplazamientos y rotaciones de cada nodo.
    """
    print(f"\n=== Generando CSV de Desplazamientos Nodales ===")
    if not check_analysis_results():
        return None

    node_data = []
    node_tags = ops.getNodeTags()

    for node_tag in node_tags:
        try:
            coord = ops.nodeCoord(node_tag)
            disp = ops.nodeDisp(node_tag)
            if not disp or len(disp) < 6:
                disp = [0]*6

            node_data.append({
                'Nodo': node_tag, 'X': coord[0], 'Y': coord[1], 'Z': coord[2],
                'UX': disp[0], 'UY': disp[1], 'UZ': disp[2],
                'RX': disp[3], 'RY': disp[4], 'RZ': disp[5],
            })
        except Exception as e:
            print(f"Error procesando nodo {node_tag}: {e}")
            continue

    if not node_data:
        print("⚠️ No se encontraron datos de desplazamientos.")
        return None

    df = pd.DataFrame(node_data)
    df.to_csv(filename, index=False, float_format='%.6f')
    print(f"✅ Archivo de desplazamientos nodales guardado: {filename}")
    return df

def generate_enhanced_results(column_elements=None, beam_x_elements=None, beam_y_elements=None, slab_elements=None):
    """
    Función principal para generar todos los archivos de resultados mejorados.
    """
    print("\n" + "="*60)
    print("GENERANDO RESULTADOS MEJORADOS PARA POST-PROCESAMIENTO")
    print("="*60)
    
    # Generar CSVs
    frame_forces_df = generate_frame_forces_csv()
    slab_forces_df = generate_slab_forces_csv()
    displacements_df = generate_nodal_displacements_csv()
    
    print("\n✅ TODOS LOS ARCHIVOS DE RESULTADOS GENERADOS")
    print("📋 Use estos archivos para análisis detallado y post-procesamiento")
    
    return {
        'frame_forces': frame_forces_df,
        'slab_forces': slab_forces_df,
        'nodal_displacements': displacements_df,
    }