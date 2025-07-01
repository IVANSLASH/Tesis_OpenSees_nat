# visualization_new.py
# ============================================
# Sistema de visualización completamente nuevo y mejorado
# para análisis estructural con OpenSeesPy
# 
# Funcionalidades:
# 1. Visualización básica con nombres de elementos y nodos
# 2. Visualización de secciones extruidas
# 3. Diagramas de solicitaciones con escala apropiada
# 4. Exportación mejorada de datos CSV
# ============================================

import openseespy.opensees as ops
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches

def plot_structure_with_labels(title="Estructura con Etiquetas"):
    """
    Crea una visualización 3D básica de la estructura mostrando:
    - Nodos con sus números
    - Elementos con sus números  
    - Líneas de conexión
    """
    print(f"\n=== GENERANDO {title.upper()} ===")
    
    try:
        # Obtener datos del modelo
        node_tags = ops.getNodeTags()
        element_tags = ops.getEleTags()
        
        if not node_tags or not element_tags:
            print("⚠️ No hay datos del modelo para visualizar")
            return None
            
        # Crear figura 3D
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Obtener coordenadas de nodos
        node_coords = {}
        x_coords, y_coords, z_coords = [], [], []
        
        for node_tag in node_tags:
            coord = ops.nodeCoord(node_tag)
            node_coords[node_tag] = coord
            x_coords.append(coord[0])
            y_coords.append(coord[1]) 
            z_coords.append(coord[2])
        
        # Plotear nodos con etiquetas
        ax.scatter(x_coords, y_coords, z_coords, c='red', s=50, alpha=0.8, label='Nodos')
        
        for node_tag, coord in node_coords.items():
            ax.text(coord[0], coord[1], coord[2], f'N{node_tag}', 
                   fontsize=8, color='red', weight='bold')
        
        # Plotear elementos con etiquetas
        for element_tag in element_tags:
            try:
                nodes = ops.eleNodes(element_tag)
                if len(nodes) >= 2:
                    coord1 = node_coords[nodes[0]]
                    coord2 = node_coords[nodes[1]]
                    
                    # Línea del elemento
                    ax.plot([coord1[0], coord2[0]], 
                           [coord1[1], coord2[1]], 
                           [coord1[2], coord2[2]], 
                           'b-', linewidth=2, alpha=0.7)
                    
                    # Etiqueta del elemento en el centro
                    mid_x = (coord1[0] + coord2[0]) / 2
                    mid_y = (coord1[1] + coord2[1]) / 2
                    mid_z = (coord1[2] + coord2[2]) / 2
                    
                    ax.text(mid_x, mid_y, mid_z, f'E{element_tag}', 
                           fontsize=7, color='blue', weight='bold')
            except:
                continue
        
        # Configurar ejes y título
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.set_zlabel('Z (m)', fontsize=12)
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # Ajustar límites con escala uniforme
        margin = 0.5
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        z_range = max(z_coords) - min(z_coords)
        
        # Usar el rango máximo para todas las dimensiones (escala uniforme)
        max_range = max(x_range, y_range, z_range)
        
        x_center = (max(x_coords) + min(x_coords)) / 2
        y_center = (max(y_coords) + min(y_coords)) / 2
        z_center = (max(z_coords) + min(z_coords)) / 2
        
        half_range = max_range / 2 + margin
        
        ax.set_xlim(x_center - half_range, x_center + half_range)
        ax.set_ylim(y_center - half_range, y_center + half_range)
        ax.set_zlim(z_center - half_range, z_center + half_range)
        
        # Asegurar escala igual en todos los ejes
        ax.set_box_aspect([1,1,1])
        
        # Leyenda
        ax.legend(loc='upper right')
        
        # Maximizar ventana
        manager = plt.get_current_fig_manager()
        try:
            manager.window.state('zoomed')
        except:
            try:
                manager.window.showMaximized()
            except:
                pass
        
        plt.tight_layout()
        
        # Guardar figura como archivo
        filename = title.lower().replace(" ", "_").replace("-", "_") + ".png"
        try:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"   💾 Imagen guardada: {filename}")
        except Exception as e:
            print(f"   ⚠️ Error guardando imagen: {e}")
        
        plt.show()
        
        print(f"✅ {title} generada exitosamente")
        print(f"   📊 {len(node_tags)} nodos, {len(element_tags)} elementos")
        
        return fig
        
    except Exception as e:
        print(f"❌ Error generando {title}: {e}")
        return None

def create_extruded_section_box(coord1, coord2, width, height, color='blue', alpha=0.7):
    """
    Crea una caja extruida que representa la sección de un elemento
    Mejorado para manejar mejor columnas y vigas
    
    Args:
        coord1, coord2: Coordenadas de extremos del elemento
        width: Ancho de la sección (en metros)
        height: Alto de la sección (en metros)  
        color: Color del elemento
        alpha: Transparencia
    """
    # Vector del elemento
    direction = np.array(coord2) - np.array(coord1)
    length = np.linalg.norm(direction)
    
    # Diagnóstico limitado
    # print(f"    Creando sección: {width*100:.0f}x{height*100:.0f} cm, longitud: {length:.2f} m")
    
    if length < 1e-6:  # Elemento muy pequeño
        return None
        
    # Vector unitario
    unit_dir = direction / length
    
    # Determinar si es columna (vertical) o viga (horizontal)
    is_column = abs(unit_dir[2]) > 0.9
    
    # Vectores perpendiculares para crear la sección
    if is_column:  # Columna vertical
        # Para columnas, usar ejes X e Y globales
        perp1 = np.array([1, 0, 0])  # Eje X
        perp2 = np.array([0, 1, 0])  # Eje Y
    else:  # Viga horizontal
        # Para vigas, crear vectores perpendiculares al elemento
        if abs(unit_dir[2]) < 0.1:  # Viga horizontal
            perp1 = np.array([0, 0, 1])  # Hacia arriba
        else:
            perp1 = np.array([1, 0, 0])
        
        perp2 = np.cross(unit_dir, perp1)
        if np.linalg.norm(perp2) > 1e-6:
            perp2 = perp2 / np.linalg.norm(perp2)
            perp1 = np.cross(perp2, unit_dir)
        else:
            perp1 = np.array([1, 0, 0])
            perp2 = np.array([0, 1, 0])
    
    # Crear vértices de la sección rectangular
    # width = ancho en plano local, height = alto en plano local
    hw, hh = width/2, height/2
    
    # print(f"      Dimensiones locales: ±{hw*100:.0f} cm (ancho), ±{hh*100:.0f} cm (alto)")
    
    # Vértices en el plano local de la sección (rectángulo)
    local_vertices = np.array([
        [-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]
    ])
    
    # Transformar vértices al espacio 3D
    section_vertices = []
    for vertex in local_vertices:
        # Transformar usando los vectores perpendiculares
        vertex_3d = vertex[0] * perp1 + vertex[1] * perp2
        section_vertices.append(vertex_3d)
    
    # Crear caras de la caja extruida
    vertices = []
    
    # Sección inicial (en coord1)
    for vertex_3d in section_vertices:
        vertices.append(np.array(coord1) + vertex_3d)
    
    # Sección final (en coord2)
    for vertex_3d in section_vertices:
        vertices.append(np.array(coord2) + vertex_3d)
    
    # Definir caras de la caja (indices de vértices)
    faces = [
        [0, 1, 2, 3],        # cara inicial
        [4, 5, 6, 7],        # cara final
        [0, 1, 5, 4],        # cara lateral 1
        [1, 2, 6, 5],        # cara lateral 2
        [2, 3, 7, 6],        # cara lateral 3
        [3, 0, 4, 7]         # cara lateral 4
    ]
    
    # Crear colección de polígonos
    face_vertices = []
    for face in faces:
        face_vertices.append([vertices[i] for i in face])
    
    return Poly3DCollection(face_vertices, alpha=alpha, facecolor=color, edgecolor='black', linewidth=0.5)

def plot_extruded_structure(section_properties, column_elements=None, beam_x_elements=None, beam_y_elements=None):
    """
    Visualiza la estructura con secciones extruidas mostrando las dimensiones reales
    Incluye volados y maneja diferentes secciones de vigas X/Y
    """
    print("\n=== GENERANDO ESTRUCTURA EXTRUIDA ===")
    
    try:
        # Obtener dimensiones de secciones
        col_width = section_properties.get("lx_col", 0.30)
        col_height = section_properties.get("ly_col", 0.60)
        
        # Dimensiones de vigas (puede ser diferentes para X e Y)
        beam_x_width = section_properties.get("b_viga_x", section_properties.get("b_viga", 0.20))
        beam_x_height = section_properties.get("h_viga_x", section_properties.get("h_viga", 0.35))
        beam_y_width = section_properties.get("b_viga_y", section_properties.get("b_viga", 0.20))
        beam_y_height = section_properties.get("h_viga_y", section_properties.get("h_viga", 0.35))
        
        print(f"  Dimensiones de secciones:")
        print(f"    Columnas: {col_width*100:.0f} x {col_height*100:.0f} cm (ancho x alto)")
        print(f"    Vigas X: {beam_x_width*100:.0f} x {beam_x_height*100:.0f} cm")
        print(f"    Vigas Y: {beam_y_width*100:.0f} x {beam_y_height*100:.0f} cm")
        
        # Diagnóstico de todas las propiedades disponibles
        print(f"  Propiedades disponibles en section_properties:")
        for key, value in section_properties.items():
            if 'col' in key or 'viga' in key:
                print(f"    {key}: {value}")
            if key in ['lx_col', 'ly_col', 'b_viga', 'h_viga']:
                print(f"    -> {key}: {value} m = {value*100:.0f} cm")
        
        # Crear figura
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Obtener TODOS los elementos del modelo (incluyendo volados)
        all_elements = ops.getEleTags()
        
        if not all_elements:
            print("⚠️ No hay elementos en el modelo")
            return None
        
        # Si no se especifican listas, clasificar todos los elementos
        if not any([column_elements, beam_x_elements, beam_y_elements]):
            column_elements = []
            beam_x_elements = []
            beam_y_elements = []
            
            # Clasificar TODOS los elementos por tipo basado en orientación
            for ele_tag in all_elements:
                try:
                    nodes = ops.eleNodes(ele_tag)
                    
                    # Solo procesar elementos lineales (vigas/columnas con 2 nodos)
                    if len(nodes) != 2:
                        print(f"    Elemento {ele_tag}: Omitido (tiene {len(nodes)} nodos, no es viga/columna)")
                        continue
                    
                    coord1 = np.array(ops.nodeCoord(nodes[0]))
                    coord2 = np.array(ops.nodeCoord(nodes[1]))
                    direction = coord2 - coord1
                    
                    # Determinar tipo de elemento
                    if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                        column_elements.append(ele_tag)  # Vertical = columna
                    elif abs(direction[0]) > abs(direction[1]):
                        beam_x_elements.append(ele_tag)  # Dirección X = viga X
                    else:
                        beam_y_elements.append(ele_tag)  # Dirección Y = viga Y
                except Exception as e:
                    print(f"    Error procesando elemento {ele_tag}: {e}")
                    continue
        
        print(f"  Elementos a mostrar:")
        print(f"    Columnas: {len(column_elements)}")
        print(f"    Vigas X: {len(beam_x_elements)}")
        print(f"    Vigas Y: {len(beam_y_elements)}")
        
        # Plotear columnas extruidas
        print(f"\n  Procesando {len(column_elements)} columnas:")
        columns_processed = 0
        for i, ele_tag in enumerate(column_elements):
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2:
                    print(f"    ⚠️ Columna {ele_tag}: Nodos incorrectos ({len(nodes)})")
                    continue
                    
                coord1 = ops.nodeCoord(nodes[0])
                coord2 = ops.nodeCoord(nodes[1])
                
                # Diagnóstico detallado para las primeras 3 columnas
                if i < 3:
                    print(f"  Columna {ele_tag}: ({coord1[0]:.1f},{coord1[1]:.1f},{coord1[2]:.1f}) → ({coord2[0]:.1f},{coord2[1]:.1f},{coord2[2]:.1f})")
                    print(f"    Usando dimensiones: {col_width*100:.0f} x {col_height*100:.0f} cm")
                
                extruded = create_extruded_section_box(coord1, coord2, col_width, col_height, 'blue', 0.7)
                if extruded:
                    ax.add_collection3d(extruded)
                    columns_processed += 1
                    if i < 3:
                        print(f"    ✅ Columna {ele_tag} visualizada")
                        
            except Exception as e:
                print(f"    ⚠️ Error visualizando columna {ele_tag}: {e}")
                continue
        
        print(f"  ✅ {columns_processed}/{len(column_elements)} columnas procesadas exitosamente")
        
        # Plotear vigas X extruidas (usando dimensiones específicas de vigas X)
        for ele_tag in beam_x_elements:
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2:
                    print(f"    ⚠️ Viga X {ele_tag}: Nodos incorrectos ({len(nodes)})")
                    continue
                    
                coord1 = ops.nodeCoord(nodes[0])
                coord2 = ops.nodeCoord(nodes[1])
                
                extruded = create_extruded_section_box(coord1, coord2, beam_x_width, beam_x_height, 'red', 0.7)
                if extruded:
                    ax.add_collection3d(extruded)
            except Exception as e:
                print(f"    ⚠️ Error visualizando viga X {ele_tag}: {e}")
                continue
        
        # Plotear vigas Y extruidas (usando dimensiones específicas de vigas Y)
        for ele_tag in beam_y_elements:
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2:
                    print(f"    ⚠️ Viga Y {ele_tag}: Nodos incorrectos ({len(nodes)})")
                    continue
                    
                coord1 = ops.nodeCoord(nodes[0])
                coord2 = ops.nodeCoord(nodes[1])
                
                extruded = create_extruded_section_box(coord1, coord2, beam_y_width, beam_y_height, 'green', 0.7)
                if extruded:
                    ax.add_collection3d(extruded)
            except Exception as e:
                print(f"    ⚠️ Error visualizando viga Y {ele_tag}: {e}")
                continue
        
        # Configurar ejes con escala uniforme
        node_tags = ops.getNodeTags()
        if node_tags:
            coords = [ops.nodeCoord(tag) for tag in node_tags]
            coords = np.array(coords)
            
            margin = 1.0
            x_range = coords[:, 0].max() - coords[:, 0].min()
            y_range = coords[:, 1].max() - coords[:, 1].min()
            z_range = coords[:, 2].max() - coords[:, 2].min()
            
            # Usar el rango máximo para todas las dimensiones (escala uniforme)
            max_range = max(x_range, y_range, z_range)
            
            x_center = (coords[:, 0].max() + coords[:, 0].min()) / 2
            y_center = (coords[:, 1].max() + coords[:, 1].min()) / 2
            z_center = (coords[:, 2].max() + coords[:, 2].min()) / 2
            
            half_range = max_range / 2 + margin
            
            ax.set_xlim(x_center - half_range, x_center + half_range)
            ax.set_ylim(y_center - half_range, y_center + half_range)
            ax.set_zlim(z_center - half_range, z_center + half_range)
            
            # Asegurar escala igual en todos los ejes
            ax.set_box_aspect([1,1,1])
        
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.set_zlabel('Z (m)', fontsize=12)
        ax.set_title('Estructura con Secciones Extruidas', fontsize=16, weight='bold', pad=20)
        
        # Leyenda con dimensiones correctas
        legend_elements = [
            mpatches.Patch(color='blue', label=f'Columnas ({col_width*100:.0f}×{col_height*100:.0f} cm)'),
            mpatches.Patch(color='red', label=f'Vigas X ({beam_x_width*100:.0f}×{beam_x_height*100:.0f} cm)'),
            mpatches.Patch(color='green', label=f'Vigas Y ({beam_y_width*100:.0f}×{beam_y_height*100:.0f} cm)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Maximizar ventana
        manager = plt.get_current_fig_manager()
        try:
            manager.window.state('zoomed')
        except:
            try:
                manager.window.showMaximized()
            except:
                pass
        
        plt.tight_layout()
        
        # Guardar figura como archivo
        filename = "estructura_extruida.png"
        try:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"   💾 Imagen guardada: {filename}")
        except Exception as e:
            print(f"   ⚠️ Error guardando imagen: {e}")
        
        plt.show()
        
        print("✅ Estructura extruida generada exitosamente")
        print(f"   🏗️ {len(column_elements)} columnas, {len(beam_x_elements)} vigas X, {len(beam_y_elements)} vigas Y")
        
        return fig
        
    except Exception as e:
        print(f"❌ Error generando estructura extruida: {e}")
        return None

def plot_force_diagram(force_type, title, scale_factor=None):
    """
    Genera un diagrama de fuerzas con escala automática optimizada
    """
    print(f"\n=== GENERANDO DIAGRAMA: {title.upper()} ===")
    
    try:
        # Obtener elementos y fuerzas
        element_tags = ops.getEleTags()
        if not element_tags:
            print("⚠️ No hay elementos para generar diagrama")
            return None
        
        # Mapeo de tipos de fuerza
        force_indices = {
            'axial': [0, 6],       # N1, N2
            'shear_y': [1, 7],     # Vy1, Vy2  
            'shear_z': [2, 8],     # Vz1, Vz2
            'moment_y': [4, 10],   # My1, My2
            'moment_z': [5, 11],   # Mz1, Mz2
            'torsion': [3, 9]      # T1, T2
        }
        
        if force_type not in force_indices:
            print(f"❌ Tipo de fuerza '{force_type}' no válido")
            return None
        
        idx1, idx2 = force_indices[force_type]
        
        # Recopilar fuerzas de todos los elementos
        forces_data = []
        max_force = 0
        
        for ele_tag in element_tags:
            try:
                # Solo procesar elementos lineales (vigas/columnas con 2 nodos)
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) != 2:
                    continue  # Omitir elementos de losa (4 nodos)
                
                forces = ops.eleForce(ele_tag)
                if forces and len(forces) >= 12:
                    force1 = forces[idx1]
                    force2 = forces[idx2]
                    
                    forces_data.append({
                        'element': ele_tag,
                        'force1': force1,
                        'force2': force2,
                        'nodes': nodes
                    })
                    
                    max_force = max(max_force, abs(force1), abs(force2))
            except Exception as e:
                print(f"    ⚠️ Error procesando elemento {ele_tag} para diagrama: {e}")
                continue
        
        if not forces_data or max_force == 0:
            print(f"⚠️ No hay datos de fuerzas válidos para {force_type}")
            return None
        
        # Calcular factor de escala automático
        if scale_factor is None:
            # Obtener dimensiones de la estructura
            node_tags = ops.getNodeTags()
            coords = [ops.nodeCoord(tag) for tag in node_tags]
            coords = np.array(coords)
            
            x_span = coords[:, 0].max() - coords[:, 0].min()
            y_span = coords[:, 1].max() - coords[:, 1].min()
            z_span = coords[:, 2].max() - coords[:, 2].min()
            
            characteristic_length = max(x_span, y_span, z_span)
            scale_factor = characteristic_length * 0.15 / max_force  # 15% de la estructura
        
        # Crear figura
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plotear estructura base (líneas delgadas)
        for data in forces_data:
            try:
                nodes = data['nodes']
                coord1 = ops.nodeCoord(nodes[0])
                coord2 = ops.nodeCoord(nodes[1])
                
                ax.plot([coord1[0], coord2[0]], 
                       [coord1[1], coord2[1]], 
                       [coord1[2], coord2[2]], 
                       'k-', linewidth=1, alpha=0.3)
            except:
                continue
        
        # Plotear diagramas de fuerza
        for data in forces_data:
            try:
                nodes = data['nodes']
                coord1 = np.array(ops.nodeCoord(nodes[0]))
                coord2 = np.array(ops.nodeCoord(nodes[1]))
                
                force1 = data['force1'] * scale_factor
                force2 = data['force2'] * scale_factor
                
                # Vector del elemento
                element_vec = coord2 - coord1
                element_length = np.linalg.norm(element_vec)
                
                if element_length > 0:
                    # Vector perpendicular para desplazar el diagrama
                    if abs(element_vec[2]) < 0.9:
                        perp = np.array([0, 0, 1])
                    else:
                        perp = np.array([1, 0, 0])
                    
                    perp = np.cross(element_vec, perp)
                    perp = perp / np.linalg.norm(perp)
                    
                    # Puntos del diagrama
                    p1 = coord1 + force1 * perp
                    p2 = coord2 + force2 * perp
                    
                    # Color según tipo de fuerza
                    colors = {
                        'axial': 'red',
                        'shear_y': 'green', 
                        'shear_z': 'blue',
                        'moment_y': 'orange',
                        'moment_z': 'purple',
                        'torsion': 'brown'
                    }
                    color = colors.get(force_type, 'black')
                    
                    # Dibujar diagrama
                    ax.plot([coord1[0], p1[0], p2[0], coord2[0]], 
                           [coord1[1], p1[1], p2[1], coord2[1]], 
                           [coord1[2], p1[2], p2[2], coord2[2]], 
                           color=color, linewidth=3, alpha=0.8)
                    
                    # Rellenar área
                    ax.plot([coord1[0], coord2[0]], [coord1[1], coord2[1]], [coord1[2], coord2[2]], 
                           color=color, linewidth=3, alpha=0.3)
                    
            except:
                continue
        
        # Configurar gráfico
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12) 
        ax.set_zlabel('Z (m)', fontsize=12)
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # Ajustar límites
        margin = max_force * scale_factor
        coords = np.array([ops.nodeCoord(tag) for tag in ops.getNodeTags()])
        ax.set_xlim(coords[:, 0].min() - margin, coords[:, 0].max() + margin)
        ax.set_ylim(coords[:, 1].min() - margin, coords[:, 1].max() + margin)
        ax.set_zlim(coords[:, 2].min() - margin, coords[:, 2].max() + margin)
        
        # Información del diagrama
        units = 'kN⋅m' if 'moment' in force_type or force_type == 'torsion' else 'kN'
        info_text = f'Escala: {scale_factor:.2e} | Unidades: {units} | Máximo: {max_force:.2f} {units}'
        ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"), verticalalignment='top')
        
        # Maximizar ventana
        manager = plt.get_current_fig_manager()
        try:
            manager.window.state('zoomed')
        except:
            try:
                manager.window.showMaximized()
            except:
                pass
        
        plt.tight_layout()
        
        # Guardar figura como archivo
        filename = f"diagrama_{force_type}.png"
        try:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"   💾 Imagen guardada: {filename}")
        except Exception as e:
            print(f"   ⚠️ Error guardando imagen: {e}")
        
        plt.show()
        
        print(f"✅ Diagrama {title} generado exitosamente")
        print(f"   📊 {len(forces_data)} elementos, Máximo: {max_force:.2f} {units}")
        
        return fig
        
    except Exception as e:
        print(f"❌ Error generando diagrama {title}: {e}")
        return None

# Variable global para mantener referencia de la figura
reference_figure = None

def generate_all_visualizations(section_properties, element_lists=None):
    """
    Genera todas las visualizaciones principales
    """
    global reference_figure
    
    print("\n" + "="*60)
    print("GENERANDO TODAS LAS VISUALIZACIONES")
    print("="*60)
    
    # 1. Estructura con etiquetas (mantener abierta como referencia)
    print("\n1️⃣ Estructura de referencia (permanece abierta)...")
    reference_figure = plot_structure_with_labels("Estructura de Referencia - USE PARA IDENTIFICAR ELEMENTOS EN CSV")
    
    # 2. Estructura extruida
    print("\n2️⃣ Estructura con secciones extruidas...")
    if element_lists:
        plot_extruded_structure(section_properties, 
                              element_lists.get('columns'), 
                              element_lists.get('beams_x'), 
                              element_lists.get('beams_y'))
    else:
        plot_extruded_structure(section_properties)
    
    # 3. Diagramas de fuerzas
    force_diagrams = [
        ('axial', 'Diagrama de Fuerzas Axiales (N)'),
        ('shear_y', 'Diagrama de Fuerzas Cortantes Y (Vy)'),
        ('shear_z', 'Diagrama de Fuerzas Cortantes Z (Vz)'),
        ('moment_y', 'Diagrama de Momentos Y (My)'),
        ('moment_z', 'Diagrama de Momentos Z (Mz)'),
        ('torsion', 'Diagrama de Momentos de Torsión (T)')
    ]
    
    for i, (force_type, title) in enumerate(force_diagrams, 3):
        print(f"\n{i}️⃣ {title}...")
        plot_force_diagram(force_type, title)
    
    # 4. Estructura deformada con escala optimizada
    print(f"\n9️⃣ Estructura deformada con escala optimizada...")
    try:
        # Usar opsvis directamente con escala optimizada
        import opsvis as opsv
        
        # Calcular escala automática optimizada
        node_tags = ops.getNodeTags()
        max_displacement = 0.0
        coords = []
        
        for tag in node_tags:
            try:
                disp = ops.nodeDisp(tag)
                coord = ops.nodeCoord(tag)
                coords.append(coord)
                total_disp = (disp[0]**2 + disp[1]**2 + disp[2]**2)**0.5
                max_displacement = max(max_displacement, total_disp)
            except:
                continue
        
        if coords and max_displacement > 0:
            coords = np.array(coords)
            structure_dimension = max(coords.max(axis=0) - coords.min(axis=0))
            scale_factor = (structure_dimension * 0.15) / max_displacement
        else:
            scale_factor = 100
        
        print(f"  📊 Desplazamiento máximo: {max_displacement:.6f} m")
        print(f"  🎯 Factor de escala aplicado: {scale_factor:.1f}")
        
        plt.figure(figsize=(16, 12))
        opsv.plot_defo(
            sfac=scale_factor,
            nep=17,
            unDefoFlag=1,
            fmt_defo={'color': 'red', 'linestyle': 'solid', 'linewidth': 2.0},
            fmt_undefo={'color': 'lightgray', 'linestyle': '--', 'linewidth': 1.0},
            az_el=(-60.0, 30.0),
            fig_wi_he=(16, 12)
        )
        plt.title(f'Estructura Deformada vs Original\nRojo: Deformada (Escala x{scale_factor:.0f}) | Gris: Original\nDesplazamiento máximo: {max_displacement:.6f} m',
                 fontsize=14, fontweight='bold')
        
        # Maximizar ventana
        try:
            mng = plt.get_current_fig_manager()
            if hasattr(mng, 'window'):
                if hasattr(mng.window, 'state'):
                    mng.window.state('zoomed')
                elif hasattr(mng.window, 'showMaximized'):
                    mng.window.showMaximized()
        except:
            pass
        
        plt.show()
        print(f"✅ Estructura deformada generada (escala optimizada: {scale_factor:.1f})")
        
    except Exception as e:
        print(f"⚠️ Error generando estructura deformada: {e}")
        print("   Intentando método alternativo...")
        try:
            # Método de respaldo
            import opsvis as opsv
            import matplotlib.pyplot as plt
            
            # Calcular escala automática
            node_tags = ops.getNodeTags()
            max_displacement = 0.0
            coords = []
            
            for tag in node_tags:
                try:
                    disp = ops.nodeDisp(tag)
                    coord = ops.nodeCoord(tag)
                    coords.append(coord)
                    total_disp = (disp[0]**2 + disp[1]**2 + disp[2]**2)**0.5
                    max_displacement = max(max_displacement, total_disp)
                except:
                    continue
            
            if coords and max_displacement > 0:
                coords = np.array(coords)
                structure_dimension = max(coords.max(axis=0) - coords.min(axis=0))
                scale_factor = (structure_dimension * 0.15) / max_displacement
            else:
                scale_factor = 100
            
            plt.figure(figsize=(16, 12))
            opsv.plot_defo(sfac=scale_factor, unDefoFlag=1)
            plt.title(f'Estructura Deformada (Escala x{scale_factor:.0f})\nDesplazamiento máximo: {max_displacement:.6f} m',
                     fontsize=14, fontweight='bold')
            plt.show()
            print(f"✅ Estructura deformada generada (escala: {scale_factor:.1f})")
        except Exception as e2:
            print(f"❌ No se pudo generar la estructura deformada: {e2}")
    
    print("\n✅ TODAS LAS VISUALIZACIONES COMPLETADAS")
    print("📋 La figura de referencia permanece abierta para consulta del CSV")

def show_reference_figure():
    """
    Muestra la figura de referencia para consulta
    """
    global reference_figure
    if reference_figure:
        plt.figure(reference_figure.number)
        plt.show()