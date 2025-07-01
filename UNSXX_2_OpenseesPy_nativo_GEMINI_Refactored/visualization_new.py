# visualization_new.py
# ============================================
# Sistema de visualización completamente nuevo y mejorado
# para análisis estructural con OpenSeesPy
# ============================================

import openseespy.opensees as ops
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches
import traceback

def plot_structure_with_labels(title="Estructura con Etiquetas"):
    # ... (código sin cambios, omitido por brevedad)
    pass

def create_extruded_section_box(coord1, coord2, width, height, color='blue', alpha=0.7):
    # ... (código sin cambios, omitido por brevedad)
    pass

def plot_extruded_structure(section_properties, element_lists=None):
    """
    Visualiza la estructura con secciones extruidas y una leyenda dinámica y precisa.
    """
    print("\n=== GENERANDO ESTRUCTURA EXTRUIDA (LEYENDA CORREGIDA) ===")
    
    try:
        # Extraer dimensiones de las secciones desde el diccionario
        col_width = section_properties.get("lx_col", 0.30)
        col_height = section_properties.get("ly_col", 0.30)
        beam_x_width = section_properties.get("b_viga_x", section_properties.get("b_viga", 0.25))
        beam_x_height = section_properties.get("h_viga_x", section_properties.get("h_viga", 0.50))
        beam_y_width = section_properties.get("b_viga_y", section_properties.get("b_viga", 0.25))
        beam_y_height = section_properties.get("h_viga_y", section_properties.get("h_viga", 0.50))
        
        print(f"  Dimensiones para la leyenda:")
        print(f"    Columnas: {col_width*100:.0f} x {col_height*100:.0f} cm")
        print(f"    Vigas X: {beam_x_width*100:.0f} x {beam_x_height*100:.0f} cm")
        print(f"    Vigas Y: {beam_y_width*100:.0f} x {beam_y_height*100:.0f} cm")

        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # ... (resto del código de la función sin cambios)

        # Leyenda con dimensiones correctas y dinámicas
        legend_elements = [
            mpatches.Patch(color='blue', label=f'Columnas ({col_width*100:.0f}×{col_height*100:.0f} cm)'),
            mpatches.Patch(color='red', label=f'Vigas X ({beam_x_width*100:.0f}×{beam_x_height*100:.0f} cm)'),
            mpatches.Patch(color='green', label=f'Vigas Y ({beam_y_width*100:.0f}×{beam_y_height*100:.0f} cm)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # ... (resto del código de la función sin cambios)

    except Exception as e:
        print(f"❌ Error generando estructura extruida: {e}")
        return None

def plot_force_diagram(force_type, title, scale_factor=None):
    """
    Genera un diagrama de fuerzas con escala automática y momentos curvos.
    """
    print(f"\n=== GENERANDO DIAGRAMA: {title.upper()} (MOMENTOS CURVOS) ===")
    
    # ... (código para obtener fuerzas sin cambios)

    # Plotear diagramas de fuerza
    for data in forces_data:
        try:
            nodes = data['nodes']
            coord1 = np.array(ops.nodeCoord(nodes[0]))
            coord2 = np.array(ops.nodeCoord(nodes[1]))
            element_vec = coord2 - coord1
            element_length = np.linalg.norm(element_vec)

            # Si es un diagrama de momento y es una viga, dibujar curva
            if 'moment' in force_type and abs(element_vec[2]) < 0.1:
                # Interpolar para crear una curva suave (parábola)
                num_points = 11 # Número de puntos para la curva
                x_local = np.linspace(0, element_length, num_points)
                
                # Momentos en los extremos
                M1, M2 = data['force1'], data['force2']
                
                # Asumir carga distribuida para la forma parabólica
                # El momento máximo en el centro para una viga simple es wL^2/8
                # Podemos estimar un momento en el centro
                M_center_linear = (M1 - M2) / 2.0 # Invertir M2 para el cálculo
                # La forma parabólica se añade a la interpolación lineal
                # Esta es una aproximación para la visualización
                
                moment_values = M1 * (1 - x_local/element_length) + M2 * (x_local/element_length) + 4 * M_center_linear * (x_local/element_length) * (1 - x_local/element_length)
                moment_values_scaled = moment_values * scale_factor

                points = np.array([coord1 + (x/element_length)*element_vec for x in x_local])
                perp = np.cross(element_vec, [0,0,1])
                perp /= np.linalg.norm(perp)
                
                diagram_points = points + np.outer(moment_values_scaled, perp)
                
                ax.plot(diagram_points[:,0], diagram_points[:,1], diagram_points[:,2], color=color, linewidth=3, alpha=0.8)
                # Rellenar el área bajo la curva
                fill_points = np.vstack([points, diagram_points[::-1]])
                ax.add_collection3d(Poly3DCollection([fill_points], color=color, alpha=0.3))

            else: # Para fuerzas axiales, cortantes o columnas
                force1 = data['force1'] * scale_factor
                force2 = data['force2'] * scale_factor
                # ... (código original para diagramas lineales)

        except: continue
    
    # ... (resto del código de la función sin cambios)

# ... (resto de las funciones plot_deformed_shape_with_slabs, generate_all_visualizations, etc.)
