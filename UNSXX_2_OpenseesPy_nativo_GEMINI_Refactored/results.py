# results.py
# ============================================
# Este módulo se encarga de la extracción, procesamiento y exportación
# de los resultados del análisis estructural. Genera tablas en formatos
# como .csv o .xlsx con las solicitaciones (fuerza axial, momento,
# cortante) y deformaciones para cada tipo de elemento (vigas, columnas,
# losas), facilitando el post-diseño.
# ============================================

import openseespy.opensees as ops
import pandas as pd

def generate_results(total_nodes, column_elements, beam_elements_x, beam_elements_y, slab_elements):
    """
    Extrae y exporta los resultados del análisis estructural.

    Args:
        total_nodes (int): Número total de nodos en el modelo.
        column_elements (list): Lista de IDs de elementos columna.
        beam_elements_x (list): Lista de IDs de elementos viga en dirección X.
        beam_elements_y (list): Lista de IDs de elementos viga en dirección Y.
        slab_elements (list): Lista de IDs de elementos losa.
    """
    print("\n=== GENERACIÓN DE RESULTADOS ===\n")

    # 1. Nodal Displacements
    print("Extrayendo desplazamientos nodales...")
    nodal_displacements = []
    for i in range(1, total_nodes + 1):
        try:
            disp = ops.nodeDisp(i)
            nodal_displacements.append({
                'Node': i,
                'Disp_X': disp[0],
                'Disp_Y': disp[1],
                'Disp_Z': disp[2],
                'Rot_X': disp[3],
                'Rot_Y': disp[4],
                'Rot_Z': disp[5]
            })
        except Exception as e:
            print(f"Error al obtener desplazamiento del nodo {i}: {e}")
    df_displacements = pd.DataFrame(nodal_displacements)
    df_displacements.to_csv('nodal_displacements.csv', index=False)
    print("Desplazamientos nodales exportados a nodal_displacements.csv")

    # 2. Element Forces (Columns and Beams) - Three points per element
    print("Extrayendo fuerzas de elementos en tres puntos (inicio, centro, final)...")
    element_forces = []

    def add_element_forces_three_points(ele_id, element_type, element_list):
        """Añade fuerzas del elemento en tres puntos: inicio, centro y final"""
        try:
            # Obtener fuerzas en los extremos del elemento
            forces = ops.eleForce(ele_id)
            
            # Para elementos 3D con 6 DOF por nodo (12 total)
            if len(forces) >= 12:
                # Fuerzas en nodo inicial (extremo 1)
                element_list.append({
                    'Element_ID': ele_id,
                    'Type': element_type,
                    'Location': 'Inicio',
                    'Axial_Force': forces[0],
                    'Shear_Y': forces[1],
                    'Shear_Z': forces[2],
                    'Torsion': forces[3],
                    'Moment_Y': forces[4],
                    'Moment_Z': forces[5]
                })
                
                # Fuerzas en el centro (aproximación por promedio)
                element_list.append({
                    'Element_ID': ele_id,
                    'Type': element_type,
                    'Location': 'Centro',
                    'Axial_Force': (forces[0] + forces[6]) / 2,
                    'Shear_Y': (forces[1] + forces[7]) / 2,
                    'Shear_Z': (forces[2] + forces[8]) / 2,
                    'Torsion': (forces[3] + forces[9]) / 2,
                    'Moment_Y': (forces[4] + forces[10]) / 2,
                    'Moment_Z': (forces[5] + forces[11]) / 2
                })
                
                # Fuerzas en nodo final (extremo 2)
                element_list.append({
                    'Element_ID': ele_id,
                    'Type': element_type,
                    'Location': 'Final',
                    'Axial_Force': forces[6],
                    'Shear_Y': forces[7],
                    'Shear_Z': forces[8],
                    'Torsion': forces[9],
                    'Moment_Y': forces[10],
                    'Moment_Z': forces[11]
                })
            else:
                # Fallback para elementos con menos DOF
                element_list.append({
                    'Element_ID': ele_id,
                    'Type': element_type,
                    'Location': 'Unico',
                    'Axial_Force': forces[0] if len(forces) > 0 else 0,
                    'Shear_Y': forces[1] if len(forces) > 1 else 0,
                    'Shear_Z': forces[2] if len(forces) > 2 else 0,
                    'Torsion': forces[3] if len(forces) > 3 else 0,
                    'Moment_Y': forces[4] if len(forces) > 4 else 0,
                    'Moment_Z': forces[5] if len(forces) > 5 else 0
                })
        except Exception as e:
            print(f"Error al obtener fuerzas del elemento {element_type.lower()} {ele_id}: {e}")

    # Columns
    for ele_id in column_elements:
        add_element_forces_three_points(ele_id, 'Column', element_forces)

    # Beams (X direction)
    for ele_id in beam_elements_x:
        add_element_forces_three_points(ele_id, 'Beam_X', element_forces)

    # Beams (Y direction)
    for ele_id in beam_elements_y:
        add_element_forces_three_points(ele_id, 'Beam_Y', element_forces)

    df_forces = pd.DataFrame(element_forces)
    df_forces.to_csv('element_forces.csv', index=False)
    print("Fuerzas de elementos (columnas y vigas) exportadas a element_forces.csv")

    # 3. Slab Results (Placeholder for future expansion)
    print("Resultados de losas (esfuerzos/deformaciones) - Implementación futura.")
    # For slabs (ShellMITC4 elements), you would typically query for stress/strain at integration points.
    # This is more complex and depends on the specific output needed for post-design.
    # Example: ops.eleResponse(ele_id, 'stress', *integration_point_args)

    # --- Puntos para escalar el código: Resultados ---
    # - Implementar la extracción de resultados para elementos de losa (esfuerzos, deformaciones).
    # - Generar reportes más detallados con gráficos y resúmenes.
    # - Exportar a otros formatos como Excel (.xlsx).
    # - Añadir funciones para verificar el cumplimiento de normativas (ej. capacidad de elementos).
