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
    """
    Genera una visualización 3D de la estructura con etiquetas de nodos y elementos.
    """
    print(f"\n=== GENERANDO VISUALIZACIÓN: {title.upper()} ===")
    
    try:
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Obtener todos los elementos
        element_tags = ops.getEleTags()
        if not element_tags:
            print("⚠️ No hay elementos para visualizar")
            return None
        
        # Dibujar elementos
        for ele_tag in element_tags:
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2: continue
                
                coord1 = np.array(ops.nodeCoord(nodes[0]))
                coord2 = np.array(ops.nodeCoord(nodes[1]))
                
                # Determinar tipo de elemento por dirección
                direction = coord2 - coord1
                if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                    color = 'blue'  # Columna
                elif abs(direction[0]) > abs(direction[1]):
                    color = 'red'   # Viga X
                else:
                    color = 'green' # Viga Y
                
                ax.plot([coord1[0], coord2[0]], [coord1[1], coord2[1]], [coord1[2], coord2[2]], 
                       color=color, linewidth=2, alpha=0.8)
                
                # Etiquetar nodos
                ax.text(coord1[0], coord1[1], coord1[2], f'N{nodes[0]}', fontsize=8)
                ax.text(coord2[0], coord2[1], coord2[2], f'N{nodes[1]}', fontsize=8)
                
            except Exception as e:
                continue
        
        # Configurar vista
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(title, fontsize=16, weight='bold')
        
        # Leyenda
        legend_elements = [
            mpatches.Patch(color='blue', label='Columnas'),
            mpatches.Patch(color='red', label='Vigas X'),
            mpatches.Patch(color='green', label='Vigas Y')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Visualización con etiquetas generada exitosamente")
        return fig
        
    except Exception as e:
        print(f"❌ Error generando visualización: {e}")
        return None

def create_extruded_section_box(coord1, coord2, width, height, color='blue', alpha=0.7):
    """
    Crea una caja extruida para representar la sección de un elemento.
    """
    try:
        element_vec = coord2 - coord1
        element_length = np.linalg.norm(element_vec)
        
        if element_length < 1e-6:
            return None
            
        # Vector unitario en dirección del elemento
        unit_vec = element_vec / element_length
        
        # Vectores perpendiculares para crear la sección
        if abs(unit_vec[2]) > 0.9:  # Elemento vertical (columna)
            perp1 = np.array([1, 0, 0])
            perp2 = np.array([0, 1, 0])
        else:  # Elemento horizontal (viga)
            perp1 = np.array([0, 0, 1])
            perp2 = np.cross(unit_vec, perp1)
            perp2 /= np.linalg.norm(perp2)
            perp1 = np.cross(perp2, unit_vec)
        
        # Crear los 8 vértices de la caja
        half_width = width / 2
        half_height = height / 2
        
        vertices = []
        for t in [0, 1]:  # Extremos del elemento
            for i in [-1, 1]:  # Ancho
                for j in [-1, 1]:  # Alto
                    vertex = coord1 + t * element_vec + i * half_width * perp1 + j * half_height * perp2
                    vertices.append(vertex)
        
        # Crear las 6 caras de la caja
        faces = [
            [0, 1, 3, 2], [4, 6, 7, 5],  # Caras extremas
            [0, 4, 5, 1], [2, 3, 7, 6],  # Caras laterales
            [0, 2, 6, 4], [1, 5, 7, 3]   # Caras superior/inferior
        ]
        
        # Crear la colección 3D
        face_vertices = [[vertices[idx] for idx in face] for face in faces]
        collection = Poly3DCollection(face_vertices, color=color, alpha=alpha)
        
        return collection
        
    except Exception as e:
        print(f"Error creando caja extruida: {e}")
        return None

def plot_extruded_structure(section_properties, element_lists=None):
    """
    Visualiza la estructura con secciones extruidas.
    """
    print("\n=== GENERANDO ESTRUCTURA EXTRUIDA ===")
    
    try:
        # Extraer dimensiones de las secciones
        col_width = section_properties.get("lx_col", 0.30)
        col_height = section_properties.get("ly_col", 0.30)
        beam_width = section_properties.get("b_viga", 0.25)
        beam_height = section_properties.get("h_viga", 0.50)
        
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Obtener elementos y clasificarlos
        element_tags = ops.getEleTags()
        column_elements = []
        beam_x_elements = []
        beam_y_elements = []
        
        for ele_tag in element_tags:
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2: continue
                
                coord1 = np.array(ops.nodeCoord(nodes[0]))
                coord2 = np.array(ops.nodeCoord(nodes[1]))
                direction = coord2 - coord1
                
                if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                    column_elements.append(ele_tag)
                elif abs(direction[0]) > abs(direction[1]):
                    beam_x_elements.append(ele_tag)
                else:
                    beam_y_elements.append(ele_tag)
            except:
                continue
        
        # Plotear columnas
        for ele_tag in column_elements:
            try:
                nodes = ops.eleNodes(ele_tag)
                coord1, coord2 = ops.nodeCoord(nodes[0]), ops.nodeCoord(nodes[1])
                extruded = create_extruded_section_box(coord1, coord2, col_width, col_height, 'blue', 0.7)
                if extruded: ax.add_collection3d(extruded)
            except: continue

        # Plotear vigas X
        for ele_tag in beam_x_elements:
            try:
                nodes = ops.eleNodes(ele_tag)
                coord1, coord2 = ops.nodeCoord(nodes[0]), ops.nodeCoord(nodes[1])
                extruded = create_extruded_section_box(coord1, coord2, beam_width, beam_height, 'red', 0.7)
                if extruded: ax.add_collection3d(extruded)
            except: continue

        # Plotear vigas Y
        for ele_tag in beam_y_elements:
            try:
                nodes = ops.eleNodes(ele_tag)
                coord1, coord2 = ops.nodeCoord(nodes[0]), ops.nodeCoord(nodes[1])
                extruded = create_extruded_section_box(coord1, coord2, beam_width, beam_height, 'green', 0.7)
                if extruded: ax.add_collection3d(extruded)
            except: continue
        
        # Configurar vista
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Estructura con Secciones Extruidas', fontsize=16, weight='bold')
        
        # Leyenda
        legend_elements = [
            mpatches.Patch(color='blue', label=f'Columnas ({col_width*100:.0f}×{col_height*100:.0f} cm)'),
            mpatches.Patch(color='red', label=f'Vigas X ({beam_width*100:.0f}×{beam_height*100:.0f} cm)'),
            mpatches.Patch(color='green', label=f'Vigas Y ({beam_width*100:.0f}×{beam_height*100:.0f} cm)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Estructura extruida generada exitosamente")
        return fig
        
    except Exception as e:
        print(f"❌ Error generando estructura extruida: {e}")
        return None

def plot_force_diagram(force_type, title, scale_factor=None):
    """
    Genera un diagrama de fuerzas con escala automática optimizada.
    """
    print(f"\n=== GENERANDO DIAGRAMA: {title.upper()} ===")
    
    try:
        element_tags = ops.getEleTags()
        if not element_tags:
            print("⚠️ No hay elementos para generar diagrama")
            return None
        
        force_indices = {
            'axial': [0, 6], 'shear_y': [1, 7], 'shear_z': [2, 8],
            'moment_y': [4, 10], 'moment_z': [5, 11], 'torsion': [3, 9]
        }
        
        if force_type not in force_indices:
            print(f"❌ Tipo de fuerza '{force_type}' no válido")
            return None
        
        idx1, idx2 = force_indices[force_type]
        
        forces_data = []
        max_force = 0
        
        for ele_tag in element_tags:
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2: continue
                
                forces = ops.eleForce(ele_tag)
                if forces and len(forces) >= 12:
                    force1, force2 = forces[idx1], forces[idx2]
                    forces_data.append({
                        'element': ele_tag, 'force1': force1, 'force2': force2, 'nodes': nodes
                    })
                    max_force = max(max_force, abs(force1), abs(force2))
            except:
                continue
        
        if not forces_data or max_force < 1e-9:
            print(f"⚠️ No hay datos de fuerzas válidos para {force_type}")
            return None
        
        if scale_factor is None:
            node_tags = ops.getNodeTags()
            coords = np.array([ops.nodeCoord(tag) for tag in node_tags])
            characteristic_length = max(coords.max(axis=0) - coords.min(axis=0))
            scale_factor = characteristic_length * 0.15 / max_force
        
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        for data in forces_data:
            try:
                nodes = data['nodes']
                coord1, coord2 = np.array(ops.nodeCoord(nodes[0])), np.array(ops.nodeCoord(nodes[1]))
                force1, force2 = data['force1'] * scale_factor, data['force2'] * scale_factor
                
                element_vec = coord2 - coord1
                if np.linalg.norm(element_vec) > 0:
                    if abs(element_vec[2]) < 0.9 * np.linalg.norm(element_vec):
                        perp = np.array([0, 0, 1])
                    else:
                        perp = np.array([1, 0, 0])
                    perp = np.cross(element_vec, perp)
                    perp /= np.linalg.norm(perp)
                    
                    p1, p2 = coord1 + force1 * perp, coord2 + force2 * perp
                    
                    colors = {'axial': 'red', 'shear_y': 'green', 'shear_z': 'blue',
                              'moment_y': 'orange', 'moment_z': 'purple', 'torsion': 'brown'}
                    color = colors.get(force_type, 'black')
                    
                    ax.plot([coord1[0], p1[0], p2[0], coord2[0]], 
                           [coord1[1], p1[1], p2[1], coord2[1]], 
                           [coord1[2], p1[2], p2[2], coord2[2]], 
                           color=color, linewidth=3, alpha=0.8)
                    ax.add_collection3d(Poly3DCollection([[coord1, p1, p2, coord2]], color=color, alpha=0.3))
            except: continue
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(title, fontsize=16, weight='bold')
        
        units = 'kN⋅m' if 'moment' in force_type or 'torsion' in force_type else 'kN'
        info_text = f'Escala: {scale_factor:.2e} | Unidades: {units} | Máximo: {max_force:.2f} {units}'
        ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"), verticalalignment='top')
        
        plt.tight_layout()
        plt.show()
        
        print(f"✅ Diagrama de {force_type} generado exitosamente")
        return fig
        
    except Exception as e:
        print(f"❌ Error generando diagrama de {force_type}: {e}")
        return None

def plot_deformed_shape_with_slabs(scale_factor=None, element_lists=None):
    """
    Genera una visualización de la estructura deformada.
    """
    print("\n=== GENERANDO ESTRUCTURA DEFORMADA ===")
    
    try:
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Obtener desplazamientos
        node_tags = ops.getNodeTags()
        if not node_tags:
            print("⚠️ No hay nodos para visualizar")
            return None
        
        # Calcular escala automática si no se proporciona
        if scale_factor is None:
            max_disp = 0
            for node in node_tags:
                try:
                    disp = ops.nodeDisp(node)
                    max_disp = max(max_disp, np.linalg.norm(disp[:3]))
                except:
                    continue
            if max_disp > 0:
                scale_factor = 1.0 / max_disp
            else:
                scale_factor = 1.0
        
        # Dibujar elementos deformados
        element_tags = ops.getEleTags()
        for ele_tag in element_tags:
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2: continue
                
                # Coordenadas originales
                coord1 = np.array(ops.nodeCoord(nodes[0]))
                coord2 = np.array(ops.nodeCoord(nodes[1]))
                
                # Desplazamientos
                disp1 = np.array(ops.nodeDisp(nodes[0]))[:3]
                disp2 = np.array(ops.nodeDisp(nodes[1]))[:3]
                
                # Coordenadas deformadas
                def_coord1 = coord1 + disp1 * scale_factor
                def_coord2 = coord2 + disp2 * scale_factor
                
                # Determinar color por tipo de elemento
                direction = coord2 - coord1
                if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                    color = 'blue'  # Columna
                elif abs(direction[0]) > abs(direction[1]):
                    color = 'red'   # Viga X
                else:
                    color = 'green' # Viga Y
                
                # Dibujar elemento original (línea punteada)
                ax.plot([coord1[0], coord2[0]], [coord1[1], coord2[1]], [coord1[2], coord2[2]], 
                       color='gray', linestyle='--', alpha=0.5, linewidth=1)
                
                # Dibujar elemento deformado
                ax.plot([def_coord1[0], def_coord2[0]], [def_coord1[1], def_coord2[1]], [def_coord1[2], def_coord2[2]], 
                       color=color, linewidth=2, alpha=0.8)
                
            except Exception as e:
                continue
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(f'Estructura Deformada (Escala: {scale_factor:.1e})', fontsize=16, weight='bold')
        
        # Leyenda
        legend_elements = [
            mpatches.Patch(color='gray', label='Posición Original'),
            mpatches.Patch(color='blue', label='Columnas'),
            mpatches.Patch(color='red', label='Vigas X'),
            mpatches.Patch(color='green', label='Vigas Y')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Estructura deformada generada exitosamente")
        return fig
        
    except Exception as e:
        print(f"❌ Error generando estructura deformada: {e}")
        return None

def generate_all_visualizations(section_properties, element_lists=None):
    """
    Genera todas las visualizaciones disponibles del modelo estructural.
    
    Args:
        section_properties (dict): Propiedades de las secciones
        element_lists (dict): Listas de elementos por tipo (opcional)
    """
    print("\n=== GENERANDO TODAS LAS VISUALIZACIONES ===")
    
    try:
        # 1. Estructura con etiquetas
        print("\n1️⃣ Generando estructura con etiquetas...")
        plot_structure_with_labels("Estructura con Etiquetas")
        
        # 2. Estructura extruida
        print("\n2️⃣ Generando estructura extruida...")
        plot_extruded_structure(section_properties, element_lists)
        
        # 3. Diagramas de fuerzas
        print("\n3️⃣ Generando diagramas de fuerzas...")
        force_types = ['axial', 'shear_y', 'moment_z']
        force_titles = ['Fuerza Axial', 'Cortante Y', 'Momento Z']
        
        for force_type, title in zip(force_types, force_titles):
            try:
                plot_force_diagram(force_type, f"Diagrama de {title}")
            except Exception as e:
                print(f"⚠️ Error en diagrama de {force_type}: {e}")
                continue
        
        # 4. Estructura deformada
        print("\n4️⃣ Generando estructura deformada...")
        plot_deformed_shape_with_slabs()
        
        print("\n✅ TODAS LAS VISUALIZACIONES GENERADAS EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error generando visualizaciones: {e}")
        traceback.print_exc()

def show_reference_figure():
    """
    Muestra una figura de referencia para consulta de elementos.
    """
    print("\n=== FIGURA DE REFERENCIA ===")
    try:
        plot_structure_with_labels("Figura de Referencia - Consulta de Elementos")
        print("✅ Figura de referencia mostrada")
    except Exception as e:
        print(f"❌ Error mostrando figura de referencia: {e}")
