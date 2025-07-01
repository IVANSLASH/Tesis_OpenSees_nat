# visualization.py
# ============================================
# Este módulo se encarga de la visualización didáctica de los resultados.
# Genera gráficos 3D de la estructura extruida, muestra solicitaciones
# y deformaciones de elementos, y visualiza la deformación de las losas
# mediante mallas. Utiliza matplotlib y opsvis para crear representaciones
# claras y comprensibles.
#
# Características principales:
# - Visualización 3D con extrusión real de secciones
# - Representación gráfica de cargas aplicadas
# - Diagramas de esfuerzos y momentos coloreados
# - Visualización de losas discretizadas
# - Comparación entre estado deformado y no deformado
# ============================================

import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Patch, FancyArrowPatch
from mpl_toolkits.mplot3d.proj3d import proj_transform
from matplotlib.patches import ConnectionPatch
import matplotlib.colors as mcolors

def plot_deformed_structure_optimized(scale_factor=None, title="Estructura Deformada con Escala Optimizada"):
    """
    Visualiza la estructura deformada con factor de escala automático optimizado.
    
    Args:
        scale_factor (float, optional): Factor de escala manual. Si None, se calcula automáticamente.
        title (str): Título del gráfico.
    
    Returns:
        tuple: (figura_matplotlib, factor_escala_usado)
    """
    print(f"\n=== {title.upper()} ===")
    
    try:
        # Obtener datos del modelo
        node_tags = ops.getNodeTags()
        if not node_tags:
            print("⚠️ No hay nodos en el modelo")
            return None, None
        
        # Calcular factor de escala automático si no se proporciona
        if scale_factor is None:
            max_displacement = 0.0
            coords = []
            
            for tag in node_tags:
                try:
                    disp = ops.nodeDisp(tag)
                    coord = ops.nodeCoord(tag)
                    coords.append(coord)
                    
                    # Calcular desplazamiento total (magnitud del vector)
                    total_disp = (disp[0]**2 + disp[1]**2 + disp[2]**2)**0.5
                    max_displacement = max(max_displacement, total_disp)
                except:
                    continue
            
            # Calcular dimensión característica de la estructura
            if coords:
                coords = np.array(coords)
                x_span = coords[:, 0].max() - coords[:, 0].min()
                y_span = coords[:, 1].max() - coords[:, 1].min()
                z_span = coords[:, 2].max() - coords[:, 2].min()
                structure_dimension = max(x_span, y_span, z_span)
                
                # Factor de escala para que deformaciones sean 15% de la estructura
                if max_displacement > 0:
                    scale_factor = (structure_dimension * 0.15) / max_displacement
                else:
                    scale_factor = 100  # Valor por defecto
            else:
                scale_factor = 100
            
            print(f"  📊 Desplazamiento máximo: {max_displacement:.6f} m")
            print(f"  📏 Dimensión de estructura: {structure_dimension:.2f} m")
            print(f"  🎯 Factor de escala calculado: {scale_factor:.1f}")
            print(f"  📐 Deformación visual: {max_displacement * scale_factor:.3f} m")
        else:
            print(f"  🎯 Factor de escala manual: {scale_factor:.1f}")
        
        # Crear figura
        fig = plt.figure(figsize=(16, 12))
        
        # Generar visualización deformada
        opsv.plot_defo(
            sfac=scale_factor,
            nep=17,
            unDefoFlag=1,  # Mostrar estructura original también
            fmt_defo={'color': 'red', 'linestyle': 'solid', 'linewidth': 2.5, 'marker': '', 'markersize': 1},
            fmt_undefo={'color': 'lightblue', 'linestyle': '--', 'linewidth': 1.5, 'marker': '.', 'markersize': 1},
            fmt_defo_faces={'alpha': 0.8, 'edgecolors': 'darkred', 'linewidths': 1.5},
            fmt_undefo_faces={'alpha': 0.3, 'edgecolors': 'blue', 'facecolors': 'lightblue', 'linestyles': 'dotted', 'linewidths': 1},
            interpFlag=1,
            endDispFlag=0,
            fmt_nodes={'color': 'black', 'linestyle': 'None', 'linewidth': 1.2, 'marker': 'o', 'markersize': 4},
            Eo=0,
            az_el=(-60.0, 30.0),
            fig_wi_he=(16, 12),
            fig_lbrt=(0.1, 0.1, 0.9, 0.9),
            node_supports=True,
            ax=False
        )
        
        # Título informativo
        plt.title(f'{title}\nRojo: Deformada (x{scale_factor:.0f}) | Azul: Original\nFactor de amplificación: {scale_factor:.1f}', 
                 fontsize=16, fontweight='bold', pad=20)
        
        # Añadir información de escala
        info_text = f'Escala de deformación: x{scale_factor:.0f}\nLas deformaciones están amplificadas para mejor visualización'
        plt.figtext(0.02, 0.02, info_text, fontsize=11,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
        
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
        
        plt.tight_layout()
        plt.show()
        
        print(f"✅ {title} generada exitosamente")
        print(f"   🎯 Factor de escala final: {scale_factor:.1f}")
        
        return fig, scale_factor
        
    except Exception as e:
        print(f"❌ Error generando {title}: {e}")
        return None, None

def plot_model_native(num_floor, total_nodes, total_elements):
    """
    Visualización nativa del modelo sin dependencia de opsvis,
    especialmente útil para mostrar volados correctamente.
    """
    print("\n=== VISUALIZACIÓN NATIVA DEL MODELO (CON VOLADOS) ===\n")
    
    try:
        # Obtener todos los nodos y elementos
        node_tags = ops.getNodeTags()
        ele_tags = ops.getEleTags()
        
        if not node_tags or not ele_tags:
            print("⚠️ No hay nodos o elementos para visualizar")
            return None
        
        # Crear figura 3D
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Obtener coordenadas de todos los nodos
        node_coords = {}
        for tag in node_tags:
            coord = ops.nodeCoord(tag)
            node_coords[tag] = coord
            # Plotear nodos
            ax.scatter(coord[0], coord[1], coord[2], c='red', s=30, alpha=0.8)
            ax.text(coord[0], coord[1], coord[2], f'  {tag}', fontsize=8)
        
        # Plotear elementos
        for ele_tag in ele_tags:
            try:
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) >= 2:
                    coord1 = node_coords[nodes[0]]
                    coord2 = node_coords[nodes[1]]
                    
                    # Línea del elemento
                    ax.plot([coord1[0], coord2[0]], 
                           [coord1[1], coord2[1]], 
                           [coord1[2], coord2[2]], 
                           'b-', linewidth=2, alpha=0.7)
                    
                    # Etiqueta del elemento
                    mid_x = (coord1[0] + coord2[0]) / 2
                    mid_y = (coord1[1] + coord2[1]) / 2
                    mid_z = (coord1[2] + coord2[2]) / 2
                    ax.text(mid_x, mid_y, mid_z, f'{ele_tag}', fontsize=7, color='blue')
            except Exception as e:
                print(f"    ⚠️ Error graficando elemento {ele_tag}: {e}")
        
        # Configurar ejes y límites
        coords_array = np.array(list(node_coords.values()))
        x_min, x_max = coords_array[:, 0].min(), coords_array[:, 0].max()
        y_min, y_max = coords_array[:, 1].min(), coords_array[:, 1].max()
        z_min, z_max = coords_array[:, 2].min(), coords_array[:, 2].max()
        
        # Añadir margen
        x_margin = max((x_max - x_min) * 0.1, 0.5)
        y_margin = max((y_max - y_min) * 0.1, 0.5)
        z_margin = max((z_max - z_min) * 0.1, 0.5)
        
        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        ax.set_zlim(z_min - z_margin, z_max + z_margin)
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(f'MODELO NATIVO CON VOLADOS - Edificio de {num_floor} plantas\n{total_nodes} nodos, {total_elements} elementos\nSistema Métrico (m, kN, s)', 
                    fontsize=14, fontweight='bold', color='darkred')
        
        # Añadir información de coordenadas
        ax.text2D(0.02, 0.98, f"Rango X: [{x_min:.1f}, {x_max:.1f}] m\nRango Y: [{y_min:.1f}, {y_max:.1f}] m\nRango Z: [{z_min:.1f}, {z_max:.1f}] m", 
                 transform=ax.transAxes, fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
        
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
        print("✓ Visualización nativa completada - volados incluidos")
        return fig
        
    except Exception as e:
        print(f"✗ Error en visualización nativa: {e}")
        return None

def plot_model_and_defo(num_floor, total_nodes, total_elements):
    """
    Visualiza el modelo estructural y su forma deformada.

    Args:
        num_floor (int): Número de pisos del edificio.
        total_nodes (int): Número total de nodos en el modelo.
        total_elements (int): Número total de elementos en el modelo.
    """
    print("\n=== VISUALIZACIÓN DEL MODELO CON ETIQUETAS ===\n")

    global reference_figure
    az_el = (-60.0, 30.0)
    fig_wi_he = (20, 15)

    # Primero intentar visualización nativa (especial para volados)
    native_fig = plot_model_native(num_floor, total_nodes, total_elements)
    
    try:
        # Crear figura de referencia con etiquetas que se mantendrá abierta
        reference_figure = plt.figure(figsize=(16, 12))
        opsv.plot_model(
            node_labels=1,  # Mostrar etiquetas de nodos
            element_labels=1,  # Mostrar etiquetas de elementos
            offset_nd_label=True,  # Desplazar etiquetas para mejor lectura
            axis_off=0,
            az_el=az_el,
            fig_wi_he=(16, 12),
            fig_lbrt=(0.1, 0.1, 0.9, 0.9),
            local_axes=False,
            nodes_only=False,
            fmt_model={'color':'blue', 'linestyle':'solid', 'linewidth':1.2, 'marker':'o', 'markersize':4},
            fmt_model_nodes_only={'color':'blue', 'linestyle':'solid', 'linewidth':1.2, 'marker':'o', 'markersize':4},
            node_supports=True,
            gauss_points=False,
            fmt_gauss_points={'color':'firebrick', 'linestyle':'None', 'linewidth':2.0, 'marker':'X', 'markersize':5},
            fmt_model_truss={'color':'green', 'linestyle':'solid', 'linewidth':1.2, 'marker':'o', 'markerfacecolor':'white'},
            truss_node_offset=0.96,
            ax=False
        )
        plt.title(f"MODELO DE REFERENCIA (OPSVIS) - Edificio de {num_floor} plantas\n{total_nodes} nodos, {total_elements} elementos\nUSE ESTA FIGURA PARA IDENTIFICAR ELEMENTOS EN EL CSV\nSistema Métrico (m, kN, s)", 
                 fontsize=14, fontweight='bold', color='darkred')
        
        # Añadir texto explicativo
        plt.figtext(0.02, 0.02, 
                   "IMPORTANTE: Esta figura permanece abierta para consulta.\n" +
                   "Use los números mostrados para identificar elementos en el archivo CSV.\n" +
                   "Nodos: círculos numerados | Elementos: números en barras\n" +
                   "NOTA: Los volados se muestran mejor en la visualización nativa anterior.",
                   fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
        
        # Maximizar la ventana de referencia
        try:
            mng = plt.get_current_fig_manager()
            if hasattr(mng, 'window'):
                if hasattr(mng.window, 'state'):
                    mng.window.state('zoomed')
                elif hasattr(mng.window, 'showMaximized'):
                    mng.window.showMaximized()
        except:
            pass
        
        # No hacer plt.show() aquí para mantener la figura abierta
        print("✓ Figura de referencia OPSVIS creada (permanece abierta para consulta)")
        print("  → Use los números mostrados para identificar elementos en el CSV")

    except Exception as e:
        print(f"✗ Error en la visualización del modelo con etiquetas: {e}")
        print("Usando solo visualización nativa...")
        if native_fig is None:
            print("Intentando visualización simple del modelo...")
            try:
                reference_figure = plt.figure(figsize=fig_wi_he)
                opsv.plot_model(node_labels=1, element_labels=1)
                plt.title(f"MODELO DE REFERENCIA - Edificio de {num_floor} plantas\nVisualización Simple con Etiquetas")
                print("✓ Visualización simple del modelo con etiquetas completada!")
            except Exception as e2:
                print(f"✗ Error en visualización simple del modelo: {e2}")
                reference_figure = None

    print("\n=== VISUALIZACIÓN DE LA FORMA DEFORMADA CON ESCALA OPTIMIZADA ===\n")
    try:
        # Calcular factor de escala automático para visualizar bien las deformaciones
        node_tags = ops.getNodeTags()
        max_displacement = 0.0
        structure_dimension = 0.0
        
        # Obtener desplazamientos máximos y dimensiones de la estructura
        coords = []
        for tag in node_tags:
            try:
                disp = ops.nodeDisp(tag)
                coord = ops.nodeCoord(tag)
                coords.append(coord)
                
                # Calcular desplazamiento total (magnitud del vector)
                total_disp = (disp[0]**2 + disp[1]**2 + disp[2]**2)**0.5
                max_displacement = max(max_displacement, total_disp)
            except:
                continue
        
        if coords:
            coords = np.array(coords)
            x_span = coords[:, 0].max() - coords[:, 0].min()
            y_span = coords[:, 1].max() - coords[:, 1].min()
            z_span = coords[:, 2].max() - coords[:, 2].min()
            structure_dimension = max(x_span, y_span, z_span)
        
        # Calcular factor de escala para que las deformaciones sean visibles (10-20% de la estructura)
        if max_displacement > 0 and structure_dimension > 0:
            optimal_scale = (structure_dimension * 0.15) / max_displacement
        else:
            optimal_scale = 100  # Factor por defecto
        
        print(f"  📊 Desplazamiento máximo: {max_displacement:.6f} m")
        print(f"  📏 Dimensión característica: {structure_dimension:.2f} m")
        print(f"  🎯 Factor de escala aplicado: {optimal_scale:.1f}")
        print(f"  📐 Deformación visual máxima: {max_displacement * optimal_scale:.3f} m ({max_displacement * optimal_scale / structure_dimension * 100:.1f}% de la estructura)")
        
        # Crear figura de forma deformada con tamaño apropiado
        plt.figure(figsize=(16, 12))
        opsv.plot_defo(
            sfac=optimal_scale,  # Usar factor de escala calculado
            nep=17,
            unDefoFlag=1,
            fmt_defo={'color': 'blue', 'linestyle': 'solid', 'linewidth': 2.0, 'marker': '', 'markersize': 1},
            fmt_undefo={'color': 'lightgray', 'linestyle': '--', 'linewidth': 1.0, 'marker': '.', 'markersize': 1},
            fmt_defo_faces={'alpha': 0.7, 'edgecolors': 'darkblue', 'linewidths': 1.5},
            fmt_undefo_faces={'alpha': 0.3, 'edgecolors': 'gray', 'facecolors': 'white', 'linestyles': 'dotted', 'linewidths': 0.8},
            interpFlag=1,
            endDispFlag=0,
            fmt_nodes={'color': 'red', 'linestyle': 'None', 'linewidth': 1.2, 'marker': 's', 'markersize': 6},
            Eo=0,
            az_el=az_el,
            fig_wi_he=(16, 12),
            fig_lbrt=(0.1, 0.1, 0.9, 0.9),
            node_supports=True,
            ax=False
        )
        plt.title(f'Forma Deformada vs. No Deformada\nAzul: Deformada (Escala x{optimal_scale:.0f}) | Gris: Original\nDesplazamiento máximo real: {max_displacement:.6f} m', 
                 fontsize=14, fontweight='bold')
        
        # Maximizar ventana de forma deformada
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
        print("✓ Visualización de la forma deformada completada exitosamente!")
    except Exception as e:
        print(f"✗ Error en la visualización de la forma deformada: {e}")
        print("Intentando visualización simple de la forma deformada...")
        try:
            # Usar el mismo cálculo de escala para el respaldo
            node_tags = ops.getNodeTags()
            max_displacement = 0.0
            structure_dimension = 0.0
            
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
            
            if coords:
                coords = np.array(coords)
                x_span = coords[:, 0].max() - coords[:, 0].min()
                y_span = coords[:, 1].max() - coords[:, 1].min()
                z_span = coords[:, 2].max() - coords[:, 2].min()
                structure_dimension = max(x_span, y_span, z_span)
            
            if max_displacement > 0 and structure_dimension > 0:
                optimal_scale = (structure_dimension * 0.15) / max_displacement
            else:
                optimal_scale = 100
            
            print(f"  🎯 Factor de escala aplicado (simple): {optimal_scale:.1f}")
            
            plt.figure(figsize=(16, 12))
            opsv.plot_defo(sfac=optimal_scale)
            plt.title(f'Forma Deformada Simple (Escala x{optimal_scale:.0f})\nDesplazamiento máximo: {max_displacement:.6f} m', 
                     fontsize=14, fontweight='bold')
            
            # Maximizar ventana simple
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
            print("✓ Visualización simple de la forma deformada completada!")
        except Exception as e2:
            print(f"✗ Error en visualización simple de la forma deformada: {e2}")


def plot_extruded_sections(geometry_data, section_properties, column_elements_ids, beam_elements_x_ids, beam_elements_y_ids):
    """
    Crea una visualización 3D que muestra las secciones de los elementos
    extruidas a lo largo de su longitud, mostrando las dimensiones reales
    de las secciones de columnas y vigas.

    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio.
        section_properties (dict): Diccionario con las propiedades de las secciones.
        column_elements_ids (list): Lista de IDs de elementos columna.
        beam_elements_x_ids (list): Lista de IDs de elementos viga en dirección X.
        beam_elements_y_ids (list): Lista de IDs de elementos viga en dirección Y.
    """
    print("\n=== GENERANDO VISUALIZACIÓN 3D DE SECCIONES EXTRUIDAS ===\n")

    lx_col = section_properties["lx_col"]
    ly_col = section_properties["ly_col"]
    b_viga = section_properties["b_viga"]
    h_viga = section_properties["h_viga"]

    Lx = sum(geometry_data["bay_widths_x"])
    Ly = sum(geometry_data["bay_widths_y"])
    Lz = sum(geometry_data["story_heights"])

    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    colores = {
        'columna': 'blue',
        'viga_x': 'red',
        'viga_y': 'green'
    }

    def crear_seccion_extruida(nodo1, nodo2, ancho, alto, color, nombre, tipo_elem=None):
        coord1 = ops.nodeCoord(nodo1)
        coord2 = ops.nodeCoord(nodo2)

        direccion = np.array(coord2) - np.array(coord1)
        longitud = np.linalg.norm(direccion)

        if longitud > 0:
            direccion_norm = direccion / longitud
        else:
            return

        puntos_seccion = np.array([
            [-ancho/2, -alto/2, 0],
            [ancho/2, -alto/2, 0],
            [ancho/2, alto/2, 0],
            [-ancho/2, alto/2, 0]
        ])

        if tipo_elem is not None and tipo_elem.startswith('viga'):
            perp1 = np.array([0, 0, 1])
            perp2 = np.cross(direccion_norm, perp1)
            perp2 = perp2 / np.linalg.norm(perp2)
            perp1 = np.cross(perp2, direccion_norm)
        else:
            if abs(direccion_norm[2]) < 0.9:
                perp1 = np.array([0, 0, 1])
            else:
                perp1 = np.array([1, 0, 0])

            perp2 = np.cross(direccion_norm, perp1)
            perp2 = perp2 / np.linalg.norm(perp2)
            perp1 = np.cross(perp2, direccion_norm)

        R = np.column_stack([perp2, perp1, direccion_norm])

        puntos_transformados = []
        for punto in puntos_seccion:
            punto_rotado = R @ punto
            puntos_transformados.append(punto_rotado)

        num_secciones = 10
        vertices = []
        caras = []

        for i in range(num_secciones + 1):
            t = i / num_secciones
            posicion = np.array(coord1) + t * direccion

            seccion_actual = []
            for punto in puntos_transformados:
                punto_final = posicion + punto
                seccion_actual.append(punto_final)
                vertices.append(punto_final)

            if i > 0:
                idx_base = len(vertices) - 2 * len(puntos_seccion)
                idx_actual = len(vertices) - len(puntos_seccion)

                for j in range(len(puntos_seccion)):
                    j_next = (j + 1) % len(puntos_seccion)
                    cara = [
                        idx_base + j,
                        idx_base + j_next,
                        idx_actual + j_next,
                        idx_actual + j
                    ]
                    caras.append(cara)

        if caras:
            poligonos = []
            for cara in caras:
                vertices_cara = [vertices[idx] for idx in cara]
                poligonos.append(vertices_cara)

            poly3d = Poly3DCollection(poligonos, alpha=0.7, facecolor=color, edgecolor='black', linewidth=0.5)
            ax.add_collection3d(poly3d)

    for elem_id in column_elements_ids:
        nodos = ops.eleNodes(elem_id)
        crear_seccion_extruida(nodos[0], nodos[1], lx_col, ly_col, colores['columna'], f'Columna {elem_id}', tipo_elem='columna')

    for elem_id in beam_elements_y_ids:
        nodos = ops.eleNodes(elem_id)
        crear_seccion_extruida(nodos[0], nodos[1], b_viga, h_viga, colores['viga_y'], f'Viga Y {elem_id}', tipo_elem='viga_y')

    for elem_id in beam_elements_x_ids:
        nodos = ops.eleNodes(elem_id)
        crear_seccion_extruida(nodos[0], nodos[1], b_viga, h_viga, colores['viga_x'], f'Viga X {elem_id}', tipo_elem='viga_x')

    # Mostrar nombre y número de cada viga sobre la extrusión
    # This part needs to be refined to correctly place text for all beams
    # For now, it's a simplified version.
    # You might need to iterate through beam_elements_x_ids and beam_elements_y_ids
    # and calculate the center of each beam.

    # Example for one beam (needs to be generalized)
    # if beam_elements_x_ids:
    #     elem_id = beam_elements_x_ids[0]
    #     nodos = ops.eleNodes(elem_id)
    #     coord1 = np.array(ops.nodeCoord(nodos[0]))
    #     coord2 = np.array(ops.nodeCoord(nodos[1]))
    #     centro = (coord1 + coord2) / 2
    #     ax.text(centro[0], centro[1], centro[2]+h_viga/2+20, f'Viga X {elem_id}', color=colores['viga_x'], fontsize=10, ha='center', va='bottom', fontweight='bold')

    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('Visualización 3D de Secciones Extruidas\nColumnas (azul), Vigas X (rojo), Vigas Y (verde)\nSistema Internacional (m, N, s)')

    # Obtener los límites reales de las coordenadas del modelo
    try:
        node_tags = ops.getNodeTags()
        if node_tags:
            coords = [ops.nodeCoord(tag) for tag in node_tags]
            coords = np.array(coords)
            
            x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
            y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
            z_min, z_max = coords[:, 2].min(), coords[:, 2].max()
            
            # Añadir un margen del 10% para mejor visualización
            x_margin = (x_max - x_min) * 0.1
            y_margin = (y_max - y_min) * 0.1
            z_margin = (z_max - z_min) * 0.1
            
            ax.set_xlim(x_min - x_margin, x_max + x_margin)
            ax.set_ylim(y_min - y_margin, y_max + y_margin)
            ax.set_zlim(z_min - z_margin, z_max + z_margin)
            
            print(f"  Coordenadas del modelo: X[{x_min:.1f}, {x_max:.1f}], Y[{y_min:.1f}, {y_max:.1f}], Z[{z_min:.1f}, {z_max:.1f}]")
        else:
            # Fallback a los límites originales si no hay nodos
            ax.set_xlim(0, Lx)
            ax.set_ylim(0, Ly)
            ax.set_zlim(0, Lz)
    except Exception as e:
        print(f"  Advertencia: No se pudieron obtener límites automáticos: {e}")
        # Usar límites basados en la geometría definida
        ax.set_xlim(0, Lx)
        ax.set_ylim(0, Ly)
        ax.set_zlim(0, Lz)

    ax.view_init(elev=20, azim=45)

    legend_elements = [
        Patch(facecolor=colores['columna'], label=f'Columnas ({lx_col:.2f}×{ly_col:.2f} m)'),
        Patch(facecolor=colores['viga_x'], label=f'Vigas X ({b_viga:.2f}×{h_viga:.2f} m)'),
        Patch(facecolor=colores['viga_y'], label=f'Vigas Y ({b_viga:.2f}×{h_viga:.2f} m)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Maximizar ventana de secciones extruidas
    try:
        mng = plt.get_current_fig_manager()
        if hasattr(mng, 'window'):
            if hasattr(mng.window, 'state'):
                mng.window.state('zoomed')
            elif hasattr(mng.window, 'showMaximized'):
                mng.window.showMaximized()
    except:
        pass

    print("✓ Visualización 3D de secciones extruidas completada exitosamente!")
    plt.tight_layout()
    plt.show()


def plot_section_details(section_properties):
    """
    Crea una visualización 2D detallada de las secciones transversales
    mostrando las dimensiones y propiedades geométricas.

    Args:
        section_properties (dict): Diccionario con las propiedades de las secciones.
    """
    print("\n=== GENERANDO DETALLES DE SECCIONES TRANSVERSALES ===\n")

    lx_col = section_properties["lx_col"]
    ly_col = section_properties["ly_col"]
    b_viga = section_properties["b_viga"]
    h_viga = section_properties["h_viga"]
    A_col = section_properties["A_col"]
    Iz_col = section_properties["Iz_col"]
    Iy_col = section_properties["Iy_col"]
    A_viga = section_properties["A_viga"]
    Iz_viga = section_properties["Iz_viga"]
    Iy_viga = section_properties["Iy_viga"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    ax1.set_aspect('equal')
    ax1.add_patch(plt.Rectangle((-lx_col/2, -ly_col/2), lx_col, ly_col,
                               facecolor='lightblue', edgecolor='blue', linewidth=2))

    ax1.plot([-lx_col/2, -lx_col/2], [-ly_col/2-20, ly_col/2+20], 'k-', linewidth=1)
    ax1.plot([lx_col/2, lx_col/2], [-ly_col/2-20, ly_col/2+20], 'k-', linewidth=1)
    ax1.plot([-lx_col/2-20, lx_col/2+20], [-ly_col/2, -ly_col/2], 'k-', linewidth=1)
    ax1.plot([-lx_col/2-20, lx_col/2+20], [ly_col/2, ly_col/2], 'k-', linewidth=1)

    ax1.text(0, -ly_col/2-0.03, f'{lx_col:.2f} m', ha='center', va='top', fontsize=12, fontweight='bold')
    ax1.text(-lx_col/2-0.03, 0, f'{ly_col:.2f} m', ha='center', va='center', fontsize=12, fontweight='bold', rotation=90)

    ax1.text(0, ly_col/2+0.05, f'Área: {A_col:.3f} m²', ha='center', va='bottom', fontsize=11)
    ax1.text(0, ly_col/2+0.03, f'Iz: {Iz_col:.6f} m⁴', ha='center', va='bottom', fontsize=11)
    ax1.text(0, ly_col/2+0.01, f'Iy: {Iy_col:.6f} m⁴', ha='center', va='bottom', fontsize=11)

    ax1.set_xlim(-lx_col/2-0.05, lx_col/2+0.05)
    ax1.set_ylim(-ly_col/2-0.05, ly_col/2+0.05)
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_title('Sección Transversal de Columna (Sistema Internacional)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    ax2.set_aspect('equal')
    ax2.add_patch(plt.Rectangle((-b_viga/2, -h_viga/2), b_viga, h_viga,
                               facecolor='lightcoral', edgecolor='red', linewidth=2))

    ax2.plot([-b_viga/2, -b_viga/2], [-h_viga/2-0.015, h_viga/2+0.015], 'k-', linewidth=1)
    ax2.plot([b_viga/2, b_viga/2], [-h_viga/2-0.015, h_viga/2+0.015], 'k-', linewidth=1)
    ax2.plot([-b_viga/2-0.015, b_viga/2+0.015], [-h_viga/2, -h_viga/2], 'k-', linewidth=1)
    ax2.plot([-b_viga/2-0.015, b_viga/2+0.015], [h_viga/2, h_viga/2], 'k-', linewidth=1)

    ax2.text(0, -h_viga/2-0.025, f'{b_viga:.2f} m', ha='center', va='top', fontsize=12, fontweight='bold')
    ax2.text(-b_viga/2-0.025, 0, f'{h_viga:.2f} m', ha='center', va='center', fontsize=12, fontweight='bold', rotation=90)

    ax2.text(0, h_viga/2+0.04, f'Área: {A_viga:.3f} m²', ha='center', va='bottom', fontsize=11)
    ax2.text(0, h_viga/2+0.02, f'Iz: {Iz_viga:.6f} m⁴', ha='center', va='bottom', fontsize=11)
    ax2.text(0, h_viga/2+0.00, f'Iy: {Iy_viga:.6f} m⁴', ha='center', va='bottom', fontsize=11)

    ax2.set_xlim(-b_viga/2-0.04, b_viga/2+0.04)
    ax2.set_ylim(-h_viga/2-0.04, h_viga/2+0.04)
    ax2.set_xlabel('X (m)')
    ax2.set_ylabel('Y (m)')
    ax2.set_title('Sección Transversal de Viga (Sistema Internacional)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_section_comparison(section_properties):
    """
    Crea una comparación visual de las secciones a escala real,
    mostrando las proporciones relativas entre columnas y vigas.

    Args:
        section_properties (dict): Diccionario con las propiedades de las secciones.
    """
    print("\n=== GENERANDO COMPARACIÓN DE SECCIONES ===\n")

    lx_col = section_properties["lx_col"]
    ly_col = section_properties["ly_col"]
    b_viga = section_properties["b_viga"]
    h_viga = section_properties["h_viga"]
    A_col = section_properties["A_col"]
    Iz_col = section_properties["Iz_col"]
    Iy_col = section_properties["Iy_col"]
    J_col = section_properties["J_col"]
    A_viga = section_properties["A_viga"]
    Iz_viga = section_properties["Iz_viga"]
    Iy_viga = section_properties["Iy_viga"]
    J_viga = section_properties["J_viga"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    ax1.set_aspect('equal')

    pos_col = (0, 0)
    pos_viga = (max(lx_col, ly_col) + 0.5, 0)  # Separar 50 cm entre secciones

    ax1.add_patch(plt.Rectangle((pos_col[0] - lx_col/2, pos_col[1] - ly_col/2),
                               lx_col, ly_col, facecolor='lightblue', edgecolor='blue', linewidth=2))
    ax1.text(pos_col[0], pos_col[1] + ly_col/2 + 0.02, 'COLUMNA', ha='center', va='bottom',
             fontsize=14, fontweight='bold', color='blue')
    ax1.text(pos_col[0], pos_col[1] - ly_col/2 - 0.02, f'{lx_col:.2f} × {ly_col:.2f} m', ha='center', va='top',
             fontsize=12, fontweight='bold')

    ax1.add_patch(plt.Rectangle((pos_viga[0] - b_viga/2, pos_viga[1] - h_viga/2),
                               b_viga, h_viga, facecolor='lightcoral', edgecolor='red', linewidth=2))
    ax1.text(pos_viga[0], pos_viga[1] + h_viga/2 + 0.02, 'VIGA', ha='center', va='bottom',
             fontsize=14, fontweight='bold', color='red')
    ax1.text(pos_viga[0], pos_viga[1] - h_viga/2 - 0.02, f'{b_viga:.2f} × {h_viga:.2f} m', ha='center', va='top',
             fontsize=12, fontweight='bold')

    escala_long = 1.0  # 1 metro de escala
    ax1.plot([pos_col[0] - lx_col/2 - 0.03, pos_col[0] - lx_col/2 - 0.03 + escala_long],
             [pos_col[1] - ly_col/2 - 0.04, pos_col[1] - ly_col/2 - 0.04], 'k-', linewidth=2)
    ax1.text(pos_col[0] - lx_col/2 - 0.03 + escala_long/2, pos_col[1] - ly_col/2 - 0.05,
             f'{escala_long:.1f} m', ha='center', va='top', fontsize=10, fontweight='bold')

    ax1.set_xlim(pos_col[0] - lx_col/2 - 0.06, pos_viga[0] + b_viga/2 + 0.06)
    ax1.set_ylim(pos_col[1] - ly_col/2 - 0.06, pos_col[1] + ly_col/2 + 0.06)
    ax1.set_title('Comparación de Secciones a Escala Real (Sistema Internacional)', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')

    propiedades = ['Área (m²)', 'Iz (m⁴)', 'Iy (m⁴)', 'J (m⁴)']
    valores_col = [A_col, Iz_col, Iy_col, J_col]
    valores_viga = [A_viga, Iz_viga, Iy_viga, J_viga]

    x = np.arange(len(propiedades))
    width = 0.35

    bars1 = ax2.bar(x - width/2, valores_col, width, label='Columna', color='lightblue', edgecolor='blue')
    bars2 = ax2.bar(x + width/2, valores_viga, width, label='Viga', color='lightcoral', edgecolor='red')

    for bar in bars1:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)

    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)

    ax2.set_xlabel('Propiedades Geométricas')
    ax2.set_ylabel('Valor')
    ax2.set_title('Comparación de Propiedades Geométricas', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(propiedades)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def plot_loads_visualization(geometry_data, load_intensities, beam_elements_x_ids, beam_elements_y_ids):
    """
    Crea una visualización 3D que muestra las cargas aplicadas al modelo.
    
    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio
        load_intensities (dict): Intensidades de carga configuradas
        beam_elements_x_ids (list): Lista de elementos viga en dirección X
        beam_elements_y_ids (list): Lista de elementos viga en dirección Y
    """
    print("\n=== GENERANDO VISUALIZACIÓN DE CARGAS APLICADAS ===\n")
    
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Dibujar estructura básica primero
    try:
        opsv.plot_model(ax=ax, node_labels=0, element_labels=0)
    except:
        # Si opsvis falla, dibujar estructura básica manualmente
        pass
    
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]
    
    # Visualizar cargas distribuidas en losas (como flechas hacia abajo)
    dead_load = load_intensities["dead_load_slab"]
    live_load = load_intensities["live_load_slab"]
    total_load = dead_load + live_load
    
    arrow_scale = total_load * 0.0001  # Escalar las flechas según la carga (ajuste para N/m²)
    
    print(f"  Dibujando cargas en losas: {total_load:.0f} N/m²")
    
    for k in range(1, num_floor + 1):  # Para cada nivel
        for j in range(num_bay_y + 1):  # Para cada posición Y
            for i in range(num_bay_x + 1):  # Para cada posición X
                # Obtener coordenadas del nodo
                try:
                    import geometry
                    node_tag = geometry.get_node_tag_from_indices(k, j, i, num_bay_x, num_bay_y)
                    coord = ops.nodeCoord(node_tag)
                    
                    # Dibujar flecha hacia abajo representando la carga
                    ax.quiver(coord[0], coord[1], coord[2], 
                             0, 0, -arrow_scale,
                             color='red', arrow_length_ratio=0.1, linewidth=2)
                except:
                    continue
    
    # Visualizar cargas distribuidas en vigas
    beam_load = load_intensities["dead_load_beam"] + load_intensities["live_load_beam"]
    print(f"  Dibujando cargas en vigas: {beam_load:.0f} N/m")
    
    # Cargas en vigas X
    for ele_id in beam_elements_x_ids:
        try:
            nodos = ops.eleNodes(ele_id)
            coord1 = np.array(ops.nodeCoord(nodos[0]))
            coord2 = np.array(ops.nodeCoord(nodos[1]))
            
            # Dibujar múltiples flechas a lo largo de la viga
            n_arrows = 5
            for i in range(n_arrows):
                t = i / (n_arrows - 1)
                pos = coord1 + t * (coord2 - coord1)
                ax.quiver(pos[0], pos[1], pos[2], 
                         0, 0, -beam_load * 0.00005,
                         color='orange', arrow_length_ratio=0.2, linewidth=1.5)
        except:
            continue
    
    # Cargas en vigas Y
    for ele_id in beam_elements_y_ids:
        try:
            nodos = ops.eleNodes(ele_id)
            coord1 = np.array(ops.nodeCoord(nodos[0]))
            coord2 = np.array(ops.nodeCoord(nodos[1]))
            
            # Dibujar múltiples flechas a lo largo de la viga
            n_arrows = 5
            for i in range(n_arrows):
                t = i / (n_arrows - 1)
                pos = coord1 + t * (coord2 - coord1)
                ax.quiver(pos[0], pos[1], pos[2], 
                         0, 0, -beam_load * 0.00005,
                         color='orange', arrow_length_ratio=0.2, linewidth=1.5)
        except:
            continue
    
    # Configurar la visualización
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('Visualización de Cargas Aplicadas (Sistema Internacional)\n' + 
                f'Losas: {total_load:.0f} N/m² | Vigas: {beam_load:.0f} N/m')
    
    # Leyenda
    legend_elements = [
        plt.Line2D([0], [0], color='red', linewidth=3, label=f'Cargas en losas ({total_load:.0f} N/m²)'),
        plt.Line2D([0], [0], color='orange', linewidth=3, label=f'Cargas en vigas ({beam_load:.0f} N/m)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()

def plot_section_force_diagrams_enhanced():
    """
    Genera diagramas 3D mejorados de fuerzas internas con colores y escalas automáticas.
    """
    print("\n=== GENERANDO DIAGRAMAS MEJORADOS DE FUERZAS INTERNAS ===\n")

    # Configurar subplots para mostrar múltiples diagramas
    fig = plt.figure(figsize=(20, 15))
    
    # Lista de componentes de fuerza para graficar
    force_components = [
        {'name': 'N', 'title': 'Fuerzas Axiales', 'scale': 0.7e-2, 'color': 'blue'},
        {'name': 'Vy', 'title': 'Fuerzas Cortantes Y', 'scale': 5e-3, 'color': 'green'},
        {'name': 'Vz', 'title': 'Fuerzas Cortantes Z', 'scale': 5e-3, 'color': 'red'},
        {'name': 'My', 'title': 'Momentos en Y', 'scale': 0.5e-3, 'color': 'orange'},
        {'name': 'Mz', 'title': 'Momentos en Z', 'scale': 0.5e-3, 'color': 'purple'},
        {'name': 'T', 'title': 'Momentos de Torsión', 'scale': 5e-2, 'color': 'brown'}
    ]
    
    for i, component in enumerate(force_components):
        ax = fig.add_subplot(2, 3, i+1, projection='3d')
        
        try:
            # Generar diagrama de fuerzas con opsvis
            opsv.section_force_diagram_3d(component['name'], component['scale'], ax=ax)
            ax.set_title(f"{component['title']} ({component['name']})", 
                        fontsize=12, fontweight='bold', color=component['color'])
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_zlabel('Z (m)')
            
            print(f"  ✅ Diagrama {component['name']} generado")
            
        except Exception as e:
            print(f"  ⚠️ Error generando diagrama {component['name']}: {e}")
            ax.text(0.5, 0.5, 0.5, f"Error en\n{component['name']}", 
                   ha='center', va='center', transform=ax.transAxes)
    
    plt.tight_layout()
    plt.suptitle('Diagramas de Fuerzas Internas y Momentos', fontsize=16, fontweight='bold', y=0.98)
    plt.show()

def plot_stress_and_moment_detailed(column_elements_ids, beam_elements_x_ids, beam_elements_y_ids):
    """
    Crea visualizaciones detalladas de esfuerzos y momentos elemento por elemento.
    
    Args:
        column_elements_ids (list): Lista de IDs de elementos columna
        beam_elements_x_ids (list): Lista de IDs de elementos viga en X
        beam_elements_y_ids (list): Lista de IDs de elementos viga en Y
    """
    print("\n=== GENERANDO ANÁLISIS DETALLADO DE ESFUERZOS Y MOMENTOS ===\n")
    
    # Extraer fuerzas de elementos
    columns_forces = []
    beams_x_forces = []
    beams_y_forces = []
    
    # Procesar columnas
    for ele_id in column_elements_ids:
        try:
            forces = ops.eleForce(ele_id)
            columns_forces.append({
                'id': ele_id,
                'N': forces[0],
                'Vy': forces[1], 
                'Vz': forces[2],
                'T': forces[3],
                'My': forces[4],
                'Mz': forces[5]
            })
        except:
            continue
    
    # Procesar vigas X
    for ele_id in beam_elements_x_ids:
        try:
            forces = ops.eleForce(ele_id)
            beams_x_forces.append({
                'id': ele_id,
                'N': forces[0],
                'Vy': forces[1],
                'Vz': forces[2], 
                'T': forces[3],
                'My': forces[4],
                'Mz': forces[5]
            })
        except:
            continue
    
    # Procesar vigas Y
    for ele_id in beam_elements_y_ids:
        try:
            forces = ops.eleForce(ele_id)
            beams_y_forces.append({
                'id': ele_id,
                'N': forces[0],
                'Vy': forces[1],
                'Vz': forces[2],
                'T': forces[3], 
                'My': forces[4],
                'Mz': forces[5]
            })
        except:
            continue
    
    # Crear gráficos de barras comparativos
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Análisis Comparativo de Esfuerzos y Momentos por Tipo de Elemento', 
                 fontsize=16, fontweight='bold')
    
    force_names = ['N (Axial)', 'Vy (Cortante Y)', 'Vz (Cortante Z)', 
                   'T (Torsión)', 'My (Momento Y)', 'Mz (Momento Z)']
    
    for i, force_name in enumerate(force_names):
        ax = axes[i//3, i%3]
        force_key = force_name.split()[0]
        
        # Extraer datos
        col_values = [abs(f[force_key]) for f in columns_forces] if columns_forces else [0]
        beam_x_values = [abs(f[force_key]) for f in beams_x_forces] if beams_x_forces else [0]
        beam_y_values = [abs(f[force_key]) for f in beams_y_forces] if beams_y_forces else [0]
        
        # Calcular estadísticas
        col_max = max(col_values) if col_values else 0
        beam_x_max = max(beam_x_values) if beam_x_values else 0
        beam_y_max = max(beam_y_values) if beam_y_values else 0
        
        col_avg = sum(col_values) / len(col_values) if col_values else 0
        beam_x_avg = sum(beam_x_values) / len(beam_x_values) if beam_x_values else 0
        beam_y_avg = sum(beam_y_values) / len(beam_y_values) if beam_y_values else 0
        
        # Gráfico de barras
        categories = ['Columnas\n(Máx)', 'Columnas\n(Prom)', 'Vigas X\n(Máx)', 
                     'Vigas X\n(Prom)', 'Vigas Y\n(Máx)', 'Vigas Y\n(Prom)']
        values = [col_max, col_avg, beam_x_max, beam_x_avg, beam_y_max, beam_y_avg]
        colors = ['darkblue', 'lightblue', 'darkred', 'lightcoral', 'darkgreen', 'lightgreen']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8)
        ax.set_title(force_name, fontweight='bold')
        ax.set_ylabel('Magnitud')
        ax.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar, value in zip(bars, values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                       f'{value:.2f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.show()
    
    # Resumen estadístico
    print("📊 RESUMEN ESTADÍSTICO DE FUERZAS:")
    print(f"  Columnas analizadas: {len(columns_forces)}")
    print(f"  Vigas X analizadas: {len(beams_x_forces)}")
    print(f"  Vigas Y analizadas: {len(beams_y_forces)}")
    
    if columns_forces:
        max_axial_col = max([abs(f['N']) for f in columns_forces])
        print(f"  Máxima fuerza axial en columnas: {max_axial_col:.2f} kN")
    
    if beams_x_forces or beams_y_forces:
        all_beam_moments = []
        if beams_x_forces:
            all_beam_moments.extend([abs(f['My']) for f in beams_x_forces])
        if beams_y_forces:
            all_beam_moments.extend([abs(f['My']) for f in beams_y_forces])
        
        if all_beam_moments:
            max_moment = max(all_beam_moments)
            print(f"  Máximo momento en vigas: {max_moment:.2f} kN⋅m")

def calculate_dynamic_scale_factors():
    """
    Calcula factores de escala dinámicos basados en las dimensiones de la estructura
    y las magnitudes de las fuerzas para que los diagramas sean proporcionales.
    """
    try:
        # Obtener dimensiones de la estructura
        node_tags = ops.getNodeTags()
        coords = [ops.nodeCoord(tag) for tag in node_tags]
        coords = np.array(coords)
        
        # Calcular dimensiones principales
        x_span = coords[:, 0].max() - coords[:, 0].min()
        y_span = coords[:, 1].max() - coords[:, 1].min()
        z_span = coords[:, 2].max() - coords[:, 2].min()
        
        # Dimensión característica (la mayor)
        characteristic_length = max(x_span, y_span, z_span)
        
        print(f"  Dimensiones estructura: X={x_span:.1f}m, Y={y_span:.1f}m, Z={z_span:.1f}m")
        print(f"  Longitud característica: {characteristic_length:.1f}m")
        
        # Analizar magnitudes de fuerzas en una muestra de elementos
        ele_tags = ops.getEleTags()
        max_forces = {'N': 0, 'Vy': 0, 'Vz': 0, 'My': 0, 'Mz': 0, 'T': 0}
        
        sample_size = min(20, len(ele_tags))  # Muestra de hasta 20 elementos
        for ele_id in ele_tags[:sample_size]:
            try:
                forces = ops.eleForce(ele_id)
                if forces and len(forces) >= 12:
                    # Fuerzas en ambos extremos del elemento
                    forces_abs = [abs(f) for f in forces]
                    max_forces['N'] = max(max_forces['N'], forces_abs[0], forces_abs[6])
                    max_forces['Vy'] = max(max_forces['Vy'], forces_abs[1], forces_abs[7])
                    max_forces['Vz'] = max(max_forces['Vz'], forces_abs[2], forces_abs[8])
                    max_forces['T'] = max(max_forces['T'], forces_abs[3], forces_abs[9])
                    max_forces['My'] = max(max_forces['My'], forces_abs[4], forces_abs[10])
                    max_forces['Mz'] = max(max_forces['Mz'], forces_abs[5], forces_abs[11])
            except:
                continue
        
        print(f"  Fuerzas máximas encontradas:")
        for key, value in max_forces.items():
            print(f"    {key}: {value:.2f}")
        
        # Calcular factores de escala para que los diagramas sean 10-15% de la dimensión característica
        target_diagram_size = characteristic_length * 0.12  # 12% de la estructura
        
        scale_factors = {}
        for force_type, max_force in max_forces.items():
            if max_force > 0:
                scale_factors[force_type] = target_diagram_size / max_force
            else:
                # Valores por defecto para fuerzas muy pequeñas
                default_scales = {'N': 1e-3, 'Vy': 1e-3, 'Vz': 1e-3, 'My': 1e-4, 'Mz': 1e-4, 'T': 1e-3}
                scale_factors[force_type] = default_scales.get(force_type, 1e-3)
        
        print(f"  Factores de escala calculados:")
        for key, value in scale_factors.items():
            print(f"    {key}: {value:.2e}")
        
        return scale_factors
        
    except Exception as e:
        print(f"  ⚠️ Error calculando factores de escala: {e}")
        # Factores por defecto más conservadores
        return {
            'N': 1e-3, 'Vy': 1e-3, 'Vz': 1e-3,
            'My': 1e-4, 'Mz': 1e-4, 'T': 1e-3
        }

def interactive_diagram_menu():
    """
    Menú interactivo para seleccionar qué diagramas de fuerzas ver.
    """
    print("\n" + "="*60)
    print("📊 MENÚ DE DIAGRAMAS DE FUERZAS INTERNAS")
    print("="*60)
    print("Seleccione el tipo de visualización:")
    print()
    print("1️⃣  Vista 3D - Todos los diagramas (automático)")
    print("2️⃣  Vista 3D - Seleccionar solicitaciones específicas")
    print("3️⃣  Vista 2D - Pórticos en dirección X")
    print("4️⃣  Vista 2D - Pórticos en dirección Y")
    print("5️⃣  Vista 2D - Seleccionar pórtico específico")
    print("6️⃣  Análisis estadístico alternativo")
    print("0️⃣  Saltar diagramas")
    print()
    
    while True:
        try:
            choice = input("Ingrese su opción (0-6): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6']:
                return choice
            else:
                print("❌ Opción inválida. Por favor ingrese un número del 0 al 6.")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada por el usuario")
            return '0'

def select_force_components():
    """
    Permite al usuario seleccionar qué componentes de fuerza visualizar.
    """
    print("\n📋 SELECCIÓN DE SOLICITACIONES")
    print("-" * 40)
    print("Seleccione las solicitaciones a visualizar:")
    print()
    print("1. N  - Fuerzas Axiales")
    print("2. Vy - Fuerzas Cortantes en Y") 
    print("3. Vz - Fuerzas Cortantes en Z")
    print("4. My - Momentos en Y")
    print("5. Mz - Momentos en Z")
    print("6. T  - Momentos de Torsión")
    print("7. Todas las anteriores")
    print()
    
    force_map = {
        '1': ('N', 'Fuerzas Axiales (N) - kN'),
        '2': ('Vy', 'Fuerzas Cortantes en Y (Vy) - kN'),
        '3': ('Vz', 'Fuerzas Cortantes en Z (Vz) - kN'),
        '4': ('My', 'Momentos en Y (My) - kN⋅m'),
        '5': ('Mz', 'Momentos en Z (Mz) - kN⋅m'),
        '6': ('T', 'Momentos de Torsión (T) - kN⋅m')
    }
    
    while True:
        try:
            selections = input("Ingrese números separados por comas (ej: 1,4,5) o 7 para todas: ").strip()
            
            if selections == '7':
                return list(force_map.values())
            
            selected_components = []
            for choice in selections.split(','):
                choice = choice.strip()
                if choice in force_map:
                    selected_components.append(force_map[choice])
                else:
                    print(f"❌ Opción '{choice}' no válida.")
                    break
            else:
                if selected_components:
                    return selected_components
                else:
                    print("❌ Debe seleccionar al menos una solicitación.")
            
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada por el usuario")
            return []

def get_frame_lines(geometry_data):
    """
    Identifica las líneas de pórticos en X e Y basándose en la geometría.
    """
    try:
        # Obtener información de la estructura
        bay_widths_x = geometry_data["bay_widths_x"]
        bay_widths_y = geometry_data["bay_widths_y"]
        
        num_bays_x = len(bay_widths_x)
        num_bays_y = len(bay_widths_y)
        
        frame_lines_x = []  # Pórticos en dirección X (paralelos al eje X)
        frame_lines_y = []  # Pórticos en dirección Y (paralelos al eje Y)
        
        # Calcular posiciones de los pórticos
        y_positions = [0]
        for width in bay_widths_y:
            y_positions.append(y_positions[-1] + width)
            
        x_positions = [0]
        for width in bay_widths_x:
            x_positions.append(x_positions[-1] + width)
        
        # Pórticos en X (líneas paralelas al eje X, en diferentes Y)
        for i, y_pos in enumerate(y_positions):
            frame_lines_x.append({
                'name': f'Pórtico X-{i+1}',
                'direction': 'X',
                'position': y_pos,
                'coordinate': 'Y'
            })
        
        # Pórticos en Y (líneas paralelas al eje Y, en diferentes X)  
        for i, x_pos in enumerate(x_positions):
            frame_lines_y.append({
                'name': f'Pórtico Y-{i+1}',
                'direction': 'Y', 
                'position': x_pos,
                'coordinate': 'X'
            })
            
        return frame_lines_x, frame_lines_y
        
    except Exception as e:
        print(f"Error identificando pórticos: {e}")
        return [], []

def plot_section_force_diagrams():
    """
    Función principal para generar diagramas de fuerzas internas con menú interactivo.
    """
    print("\n=== GENERANDO DIAGRAMAS DE FUERZAS INTERNAS ===\n")
    
    # Verificar que el modelo tenga elementos
    try:
        ele_tags = ops.getEleTags()
        if not ele_tags or len(ele_tags) == 0:
            print("  ⚠️ No hay elementos en el modelo. No se pueden generar diagramas.")
            return
        
        print(f"  Encontrados {len(ele_tags)} elementos en el modelo")
        
        # Verificar elementos válidos
        valid_elements = []
        for ele_id in ele_tags[:5]:
            try:
                forces = ops.eleForce(ele_id)
                if forces and len(forces) >= 12:
                    valid_elements.append(ele_id)
            except:
                continue
        
        if not valid_elements:
            print("  ⚠️ No hay elementos válidos para diagramas 3D")
            print("  Generando diagramas alternativos...")
            plot_alternative_force_diagrams()
            return
            
    except Exception as e:
        print(f"  ⚠️ Error verificando el modelo: {e}")
        plot_alternative_force_diagrams()
        return
    
    # Mostrar menú interactivo
    choice = interactive_diagram_menu()
    
    if choice == '0':
        print("⏩ Generación de diagramas omitida por el usuario")
        return
    elif choice == '1':
        generate_all_3d_diagrams()
    elif choice == '2':
        generate_selected_3d_diagrams()
    elif choice == '3':
        generate_2d_frame_diagrams('X')
    elif choice == '4':
        generate_2d_frame_diagrams('Y')
    elif choice == '5':
        generate_specific_frame_diagram()
    elif choice == '6':
        plot_alternative_force_diagrams()

def generate_all_3d_diagrams():
    """
    Genera todos los diagramas 3D automáticamente.
    """
    print("\n📊 Generando todos los diagramas 3D...")
    
    scale_factors = calculate_dynamic_scale_factors()
    diagrams = [
        ('N', scale_factors['N'], 'Diagrama 3D - Fuerzas Axiales (N)', 'kN'),
        ('Vy', scale_factors['Vy'], 'Diagrama 3D - Fuerzas Cortantes en Y (Vy)', 'kN'),
        ('Vz', scale_factors['Vz'], 'Diagrama 3D - Fuerzas Cortantes en Z (Vz)', 'kN'),
        ('My', scale_factors['My'], 'Diagrama 3D - Momentos en Y (My)', 'kN⋅m'),
        ('Mz', scale_factors['Mz'], 'Diagrama 3D - Momentos en Z (Mz)', 'kN⋅m'),
        ('T', scale_factors['T'], 'Diagrama 3D - Momentos de Torsión (T)', 'kN⋅m')
    ]
    
    successful = 0
    for diagram_type, scale_factor, title, units in diagrams:
        if generate_single_3d_diagram(diagram_type, scale_factor, title, units):
            successful += 1
    
    print(f"\n✅ {successful}/{len(diagrams)} diagramas 3D generados exitosamente")

def generate_selected_3d_diagrams():
    """
    Genera diagramas 3D seleccionados por el usuario.
    """
    selected_components = select_force_components()
    if not selected_components:
        print("⏩ No se seleccionaron componentes")
        return
    
    print(f"\n📊 Generando {len(selected_components)} diagramas 3D seleccionados...")
    
    scale_factors = calculate_dynamic_scale_factors()
    successful = 0
    
    for force_type, title in selected_components:
        scale_factor = scale_factors.get(force_type, 1e-3)
        units = 'kN⋅m' if force_type in ['My', 'Mz', 'T'] else 'kN'
        full_title = f"Diagrama 3D - {title}"
        
        if generate_single_3d_diagram(force_type, scale_factor, full_title, units):
            successful += 1
    
    print(f"\n✅ {successful}/{len(selected_components)} diagramas seleccionados generados exitosamente")

def generate_single_3d_diagram(diagram_type, scale_factor, title, units):
    """
    Genera un solo diagrama 3D.
    """
    try:
        print(f"  📈 {diagram_type}: {title}")
        
        fig = plt.figure(figsize=(16, 12))
        opsv.section_force_diagram_3d(diagram_type, scale_factor)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.figtext(0.02, 0.02, f'Escala: {scale_factor:.2e} | Unidades: {units}', 
                   fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        # Maximizar ventana
        try:
            mng = plt.get_current_fig_manager()
            if hasattr(mng, 'window') and hasattr(mng.window, 'state'):
                mng.window.state('zoomed')
        except:
            pass
            
        plt.show()
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def extract_frame_elements(direction, coordinate=None, tolerance=0.1):
    """
    Extrae elementos que pertenecen a un pórtico específico.
    
    Args:
        direction: 'X' o 'Y' - dirección del pórtico
        coordinate: coordenada específica del pórtico (opcional)
        tolerance: tolerancia para considerar elementos en el mismo pórtico
    """
    try:
        ele_tags = ops.getEleTags()
        frame_elements = []
        
        for ele_id in ele_tags:
            try:
                nodes = ops.eleNodes(ele_id)
                if len(nodes) >= 2:
                    coord1 = np.array(ops.nodeCoord(nodes[0]))
                    coord2 = np.array(ops.nodeCoord(nodes[1]))
                    
                    if direction == 'X':
                        # Pórticos X: elementos que tienen la misma coordenada Y
                        if coordinate is not None:
                            if (abs(coord1[1] - coordinate) <= tolerance and 
                                abs(coord2[1] - coordinate) <= tolerance):
                                frame_elements.append({
                                    'id': ele_id,
                                    'nodes': nodes,
                                    'coord1': coord1,
                                    'coord2': coord2,
                                    'length': np.linalg.norm(coord2 - coord1)
                                })
                        else:
                            # Todos los elementos predominantemente en X
                            direction_vec = coord2 - coord1
                            if abs(direction_vec[0]) > max(abs(direction_vec[1]), abs(direction_vec[2])):
                                frame_elements.append({
                                    'id': ele_id,
                                    'nodes': nodes,
                                    'coord1': coord1,
                                    'coord2': coord2,
                                    'length': np.linalg.norm(direction_vec)
                                })
                    
                    elif direction == 'Y':
                        # Pórticos Y: elementos que tienen la misma coordenada X
                        if coordinate is not None:
                            if (abs(coord1[0] - coordinate) <= tolerance and 
                                abs(coord2[0] - coordinate) <= tolerance):
                                frame_elements.append({
                                    'id': ele_id,
                                    'nodes': nodes,
                                    'coord1': coord1,
                                    'coord2': coord2,
                                    'length': np.linalg.norm(coord2 - coord1)
                                })
                        else:
                            # Todos los elementos predominantemente en Y
                            direction_vec = coord2 - coord1
                            if abs(direction_vec[1]) > max(abs(direction_vec[0]), abs(direction_vec[2])):
                                frame_elements.append({
                                    'id': ele_id,
                                    'nodes': nodes,
                                    'coord1': coord1,
                                    'coord2': coord2,
                                    'length': np.linalg.norm(direction_vec)
                                })
                                
            except Exception as e:
                continue
                
        return frame_elements
        
    except Exception as e:
        print(f"Error extrayendo elementos del pórtico: {e}")
        return []

def plot_2d_force_diagram_native(elements, force_type, title, direction):
    """
    Genera un diagrama 2D nativo usando matplotlib directamente.
    """
    try:
        if not elements:
            print(f"    ⚠️ No hay elementos en el pórtico para {force_type}")
            return False
            
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Mapeo de componentes de fuerza
        force_mapping = {
            'N': (0, 6),    # Fuerza axial nodo 1, nodo 2
            'Vy': (1, 7),   # Fuerza cortante Y nodo 1, nodo 2
            'Vz': (2, 8),   # Fuerza cortante Z nodo 1, nodo 2
            'My': (4, 10),  # Momento Y nodo 1, nodo 2
            'Mz': (5, 11),  # Momento Z nodo 1, nodo 2
            'T': (3, 9)     # Torsión nodo 1, nodo 2
        }
        
        if force_type not in force_mapping:
            print(f"    ⚠️ Tipo de fuerza {force_type} no reconocido")
            return False
            
        idx1, idx2 = force_mapping[force_type]
        
        max_force = 0
        elements_data = []
        
        # Extraer fuerzas de todos los elementos
        for elem in elements:
            try:
                forces = ops.eleForce(elem['id'])
                if forces and len(forces) >= 12:
                    force1 = forces[idx1] if len(forces) > idx1 else 0
                    force2 = forces[idx2] if len(forces) > idx2 else 0
                    
                    elements_data.append({
                        'element': elem,
                        'force1': force1,
                        'force2': force2,
                        'force_max': max(abs(force1), abs(force2))
                    })
                    
                    max_force = max(max_force, abs(force1), abs(force2))
                    
            except Exception as e:
                continue
        
        if not elements_data or max_force == 0:
            print(f"    ⚠️ No hay datos de fuerza válidos para {force_type}")
            return False
        
        # Calcular factor de escala para visualización
        # Obtener dimensiones del pórtico
        all_coords = []
        for elem_data in elements_data:
            all_coords.extend([elem_data['element']['coord1'], elem_data['element']['coord2']])
        
        coords_array = np.array(all_coords)
        if direction == 'X':
            span = coords_array[:, 0].max() - coords_array[:, 0].min()
            height = coords_array[:, 2].max() - coords_array[:, 2].min()
        else:
            span = coords_array[:, 1].max() - coords_array[:, 1].min()
            height = coords_array[:, 2].max() - coords_array[:, 2].min()
        
        characteristic_length = max(span, height)
        scale_factor = characteristic_length * 0.2 / max_force if max_force > 0 else 1e-3
        
        # Dibujar elementos y diagramas
        for elem_data in elements_data:
            elem = elem_data['element']
            force1 = elem_data['force1']
            force2 = elem_data['force2']
            
            # Coordenadas del elemento
            if direction == 'X':
                x1, z1 = elem['coord1'][0], elem['coord1'][2]
                x2, z2 = elem['coord2'][0], elem['coord2'][2]
            else:
                x1, z1 = elem['coord1'][1], elem['coord1'][2]
                x2, z2 = elem['coord2'][1], elem['coord2'][2]
            
            # Dibujar elemento (línea de referencia)
            ax.plot([x1, x2], [z1, z2], 'k-', linewidth=2, alpha=0.7)
            
            # Dibujar diagrama de fuerzas
            if force_type in ['N']:  # Fuerzas axiales - diagramas rectangulares
                force_avg = (force1 + force2) / 2
                offset = force_avg * scale_factor
                
                # Vector perpendicular al elemento
                elem_vec = np.array([x2 - x1, z2 - z1])
                elem_length = np.linalg.norm(elem_vec)
                if elem_length > 0:
                    perp_vec = np.array([-elem_vec[1], elem_vec[0]]) / elem_length
                    
                    # Puntos del diagrama
                    p1 = np.array([x1, z1]) + offset * perp_vec
                    p2 = np.array([x2, z2]) + offset * perp_vec
                    
                    # Dibujar diagrama
                    color = 'red' if force_avg > 0 else 'blue'
                    ax.plot([x1, p1[0], p2[0], x2], [z1, p1[1], p2[1], z2], 
                           color=color, linewidth=2)
                    ax.fill([x1, p1[0], p2[0], x2], [z1, p1[1], p2[1], z2], 
                           color=color, alpha=0.3)
                    
            else:  # Cortantes y momentos - diagramas trapezoidales/triangulares
                # Crear diagrama más detallado
                n_points = 10
                for i in range(n_points):
                    t = i / (n_points - 1)
                    
                    # Interpolación linear de fuerzas
                    force_at_t = force1 * (1 - t) + force2 * t
                    offset = force_at_t * scale_factor
                    
                    # Punto en el elemento
                    x_t = x1 * (1 - t) + x2 * t
                    z_t = z1 * (1 - t) + z2 * t
                    
                    # Vector perpendicular
                    elem_vec = np.array([x2 - x1, z2 - z1])
                    elem_length = np.linalg.norm(elem_vec)
                    if elem_length > 0:
                        perp_vec = np.array([-elem_vec[1], elem_vec[0]]) / elem_length
                        
                        # Punto del diagrama
                        diagram_point = np.array([x_t, z_t]) + offset * perp_vec
                        
                        if i == 0:
                            x_diagram = [x_t, diagram_point[0]]
                            z_diagram = [z_t, diagram_point[1]]
                        else:
                            x_diagram.extend([diagram_point[0]])
                            z_diagram.extend([diagram_point[1]])
                
                # Cerrar el diagrama
                x_diagram.append(x2)
                z_diagram.append(z2)
                
                # Dibujar
                color = 'green' if force_type in ['Vy', 'Vz'] else 'purple'
                ax.plot(x_diagram, z_diagram, color=color, linewidth=2)
                ax.fill(x_diagram, z_diagram, color=color, alpha=0.3)
            
            # Etiqueta del elemento
            mid_x = (x1 + x2) / 2
            mid_z = (z1 + z2) / 2
            ax.text(mid_x, mid_z, str(elem['id']), fontsize=8, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
        
        # Configurar ejes y títulos
        ax.set_xlabel(f'{"X" if direction == "X" else "Y"} (m)', fontsize=12)
        ax.set_ylabel('Z (m)', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # Información adicional
        units = 'kN⋅m' if force_type in ['My', 'Mz', 'T'] else 'kN'
        ax.text(0.02, 0.98, f'Escala: {scale_factor:.2e} | Unidades: {units} | Elementos: {len(elements_data)}',
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
        
        # Maximizar ventana
        try:
            mng = plt.get_current_fig_manager()
            if hasattr(mng, 'window') and hasattr(mng.window, 'state'):
                mng.window.state('zoomed')
        except:
            pass
            
        plt.tight_layout()
        plt.show()
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error generando diagrama nativo: {e}")
        return False

def generate_2d_frame_diagrams(direction):
    """
    Genera diagramas 2D nativos para todos los pórticos en una dirección específica.
    """
    try:
        print(f"\n📐 Generando diagramas 2D nativos de pórticos en dirección {direction}")
        
        # Seleccionar qué solicitaciones mostrar
        selected_components = select_force_components()
        if not selected_components:
            print("⏩ No se seleccionaron componentes")
            return
        
        # Extraer elementos del pórtico en la dirección especificada
        elements = extract_frame_elements(direction)
        
        if not elements:
            print(f"    ⚠️ No se encontraron elementos en pórticos dirección {direction}")
            return
            
        print(f"    📊 Encontrados {len(elements)} elementos en pórticos {direction}")
        
        successful = 0
        # Para cada componente seleccionado, crear diagrama 2D nativo
        for force_type, title in selected_components:
            try:
                print(f"  📈 Generando diagrama 2D nativo - {title}")
                
                diagram_title = f'Pórticos en {direction} - {title}'
                
                if plot_2d_force_diagram_native(elements, force_type, diagram_title, direction):
                    successful += 1
                
            except Exception as e:
                print(f"    ❌ Error generando diagrama 2D {force_type}: {e}")
                continue
        
        print(f"\n✅ {successful}/{len(selected_components)} diagramas 2D nativos generados exitosamente")
                
    except Exception as e:
        print(f"❌ Error en diagramas 2D nativos: {e}")

def generate_specific_frame_diagram():
    """
    Permite al usuario seleccionar un pórtico específico para visualizar.
    """
    print("\n🏗️ SELECCIÓN DE PÓRTICO ESPECÍFICO")
    print("-" * 50)
    
    try:
        # Obtener información básica del modelo
        node_tags = ops.getNodeTags()
        coords = [ops.nodeCoord(tag) for tag in node_tags]
        coords = np.array(coords)
        
        # Identificar posiciones únicas en X e Y
        x_positions = sorted(list(set(coords[:, 0])))
        y_positions = sorted(list(set(coords[:, 1])))
        
        print("Pórticos disponibles:")
        print()
        print("📍 PÓRTICOS EN DIRECCIÓN X (paralelos al eje X):")
        for i, y_pos in enumerate(y_positions):
            print(f"   X{i+1}: Y = {y_pos:.1f} m")
        
        print()
        print("📍 PÓRTICOS EN DIRECCIÓN Y (paralelos al eje Y):")
        for i, x_pos in enumerate(x_positions):
            print(f"   Y{i+1}: X = {x_pos:.1f} m")
        
        print()
        print("Ejemplos de selección:")
        print("  - 'X1' para primer pórtico en dirección X")
        print("  - 'Y3' para tercer pórtico en dirección Y")
        print()
        
        while True:
            try:
                selection = input("Seleccione un pórtico (ej: X1, Y2): ").strip().upper()
                
                if selection.startswith('X') and len(selection) > 1:
                    try:
                        frame_num = int(selection[1:]) - 1
                        if 0 <= frame_num < len(y_positions):
                            y_coord = y_positions[frame_num]
                            generate_single_frame_diagram('X', frame_num + 1, y_coord)
                            return
                        else:
                            print(f"❌ Pórtico X{frame_num + 1} no existe. Disponibles: X1 a X{len(y_positions)}")
                    except ValueError:
                        print("❌ Formato inválido. Use formato X1, X2, etc.")
                        
                elif selection.startswith('Y') and len(selection) > 1:
                    try:
                        frame_num = int(selection[1:]) - 1
                        if 0 <= frame_num < len(x_positions):
                            x_coord = x_positions[frame_num]
                            generate_single_frame_diagram('Y', frame_num + 1, x_coord)
                            return
                        else:
                            print(f"❌ Pórtico Y{frame_num + 1} no existe. Disponibles: Y1 a Y{len(x_positions)}")
                    except ValueError:
                        print("❌ Formato inválido. Use formato Y1, Y2, etc.")
                else:
                    print("❌ Formato inválido. Use X1, X2, Y1, Y2, etc.")
                    
            except KeyboardInterrupt:
                print("\n⚠️ Selección cancelada")
                return
                
    except Exception as e:
        print(f"❌ Error obteniendo información de pórticos: {e}")

def generate_single_frame_diagram(direction, frame_number, coordinate):
    """
    Genera diagrama nativo para un pórtico específico.
    """
    print(f"\n🎯 Generando diagramas nativos para Pórtico {direction}{frame_number}")
    print(f"   Coordenada: {'Y' if direction == 'X' else 'X'} = {coordinate:.1f} m")
    
    # Seleccionar componentes
    selected_components = select_force_components()
    if not selected_components:
        print("⏩ No se seleccionaron componentes")
        return
    
    # Extraer elementos específicos del pórtico
    elements = extract_frame_elements(direction, coordinate)
    
    if not elements:
        print(f"    ⚠️ No se encontraron elementos en Pórtico {direction}{frame_number}")
        return
    
    print(f"    📊 Encontrados {len(elements)} elementos en el pórtico")
    
    successful = 0
    
    for force_type, title in selected_components:
        try:
            print(f"  📈 Generando diagrama nativo - {force_type}: {title}")
            
            # Configurar título específico del pórtico
            if direction == 'X':
                view_desc = f"Pórtico X{frame_number} (Y={coordinate:.1f}m)"
            else:
                view_desc = f"Pórtico Y{frame_number} (X={coordinate:.1f}m)"
            
            diagram_title = f'{view_desc} - {title}'
            
            # Generar diagrama nativo
            if plot_2d_force_diagram_native(elements, force_type, diagram_title, direction):
                successful += 1
            
        except Exception as e:
            print(f"    ❌ Error generando {force_type}: {e}")
            continue
    
    print(f"\n✅ {successful}/{len(selected_components)} diagramas del pórtico generados exitosamente")

def plot_alternative_force_diagrams():
    """
    Método alternativo para generar diagramas de fuerzas cuando opsvis falla.
    """
    print("\n=== GENERANDO DIAGRAMAS ALTERNATIVOS DE FUERZAS ===\n")
    
    try:
        # Usar el método existing plot_stress_and_moment_detailed 
        print("  Generando análisis estadístico de fuerzas...")
        
        # Obtener elementos por tipo desde el modelo
        ele_tags = ops.getEleTags()
        if not ele_tags:
            print("  ⚠️ No hay elementos en el modelo")
            return
            
        # Clasificar elementos por tipo basado en sus fuerzas
        column_elements = []
        beam_elements_x = []
        beam_elements_y = []
        
        for ele_id in ele_tags:
            try:
                # Obtener nodos del elemento
                nodes = ops.eleNodes(ele_id)
                if len(nodes) >= 2:
                    coord1 = np.array(ops.nodeCoord(nodes[0]))
                    coord2 = np.array(ops.nodeCoord(nodes[1]))
                    direction = coord2 - coord1
                    
                    # Clasificar por dirección predominante
                    if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                        column_elements.append(ele_id)
                    elif abs(direction[0]) > abs(direction[1]):
                        beam_elements_x.append(ele_id)
                    else:
                        beam_elements_y.append(ele_id)
            except:
                continue
        
        print(f"  Elementos clasificados: {len(column_elements)} columnas, {len(beam_elements_x)} vigas-X, {len(beam_elements_y)} vigas-Y")
        
        # Generar diagramas alternativos
        plot_stress_and_moment_detailed(column_elements, beam_elements_x, beam_elements_y)
        
    except Exception as e:
        print(f"  ⚠️ Error en diagramas alternativos: {e}")
        print("  Los resultados están disponibles en el archivo CSV")

def show_reference_figure():
    """
    Muestra la figura de referencia al final del proceso para consulta del CSV.
    """
    try:
        if 'reference_figure' in globals() and reference_figure is not None:
            print("\n=== FIGURA DE REFERENCIA PARA CONSULTA DEL CSV ===")
            print("📋 Mostrando figura de referencia con números de elementos y nodos")
            print("   Use esta figura para identificar elementos en el archivo CSV")
            plt.figure(reference_figure.number)
            plt.show()
        else:
            print("⚠️ Figura de referencia no disponible")
    except Exception as e:
        print(f"⚠️ Error mostrando figura de referencia: {e}")

    # --- Puntos para escalar el código: Visualización ---
    # Se pueden añadir más tipos de visualizaciones (ej. reacciones en apoyos, esfuerzos en losas).
    # Mejorar la interactividad de los gráficos.
    # Exportar gráficos a diferentes formatos.
