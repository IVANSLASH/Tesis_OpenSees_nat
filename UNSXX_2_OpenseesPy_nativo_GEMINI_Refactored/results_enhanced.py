# results_enhanced.py
# ============================================
# Sistema mejorado de generación de resultados y archivos CSV
# con información detallada para post-procesamiento
# ============================================

import openseespy.opensees as ops
import pandas as pd
import numpy as np
from datetime import datetime

def generate_detailed_element_csv(filename="detailed_elements.csv"):
    """
    Genera CSV con información detallada de elementos incluyendo:
    - Número de elemento
    - Nodos de inicio y final
    - Coordenadas de nodos
    - Tipo de elemento (columna, viga X, viga Y)
    - Fuerzas en tres puntos (inicio, centro, final)
    """
    print(f"\n=== GENERANDO CSV DETALLADO DE ELEMENTOS ===")
    
    try:
        element_tags = ops.getEleTags()
        if not element_tags:
            print("⚠️ No hay elementos para exportar")
            return None
        
        # Lista para almacenar datos
        element_data = []
        
        for ele_tag in element_tags:
            try:
                # Obtener nodos del elemento
                nodes = ops.eleNodes(ele_tag)
                if len(nodes) < 2:
                    continue
                
                # Determinar si es elemento lineal (viga/columna) o shell (losa)
                if len(nodes) == 2:
                    # Elemento lineal (viga/columna)
                    node_i = nodes[0]
                    node_j = nodes[1]
                    
                    # Coordenadas de nodos
                    coord_i = ops.nodeCoord(node_i)
                    coord_j = ops.nodeCoord(node_j)
                    
                    # Determinar tipo de elemento
                    direction = np.array(coord_j) - np.array(coord_i)
                    if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                        element_type = "Columna"
                    elif abs(direction[0]) > abs(direction[1]):
                        element_type = "Viga_X"
                    else:
                        element_type = "Viga_Y"
                    
                    # Longitud del elemento
                    length = np.linalg.norm(direction)
                    
                elif len(nodes) == 4:
                    # Elemento shell (losa) - saltar en esta función
                    print(f"    Elemento {ele_tag}: Losa (4 nodos) - omitido en análisis de vigas/columnas")
                    continue
                else:
                    # Otro tipo de elemento
                    print(f"    Elemento {ele_tag}: Tipo desconocido ({len(nodes)} nodos) - omitido")
                    continue
                
                # Obtener fuerzas del elemento (solo para elementos lineales)
                try:
                    forces = ops.eleForce(ele_tag)
                except Exception as e:
                    print(f"    ⚠️ Error obteniendo fuerzas del elemento {ele_tag}: {e}")
                    forces = None
                
                if forces and len(forces) >= 12:
                    # Fuerzas en nodo i (inicio)
                    Ni = forces[0]    # Axial
                    Vyi = forces[1]   # Cortante Y
                    Vzi = forces[2]   # Cortante Z
                    Ti = forces[3]    # Torsión
                    Myi = forces[4]   # Momento Y
                    Mzi = forces[5]   # Momento Z
                    
                    # Fuerzas en nodo j (final)
                    Nj = forces[6]    # Axial
                    Vyj = forces[7]   # Cortante Y
                    Vzj = forces[8]   # Cortante Z
                    Tj = forces[9]    # Torsión
                    Myj = forces[10]  # Momento Y
                    Mzj = forces[11]  # Momento Z
                    
                    # Calcular fuerzas en el centro (aproximación lineal)
                    Nc = (Ni + Nj) / 2
                    Vyc = (Vyi + Vyj) / 2
                    Vzc = (Vzi + Vzj) / 2
                    Tc = (Ti + Tj) / 2
                    Myc = (Myi + Myj) / 2
                    Mzc = (Mzi + Mzj) / 2
                    
                else:
                    # Si no hay fuerzas, llenar con ceros
                    Ni = Vyi = Vzi = Ti = Myi = Mzi = 0
                    Nj = Vyj = Vzj = Tj = Myj = Mzj = 0
                    Nc = Vyc = Vzc = Tc = Myc = Mzc = 0
                
                # Agregar datos del elemento
                element_data.append({
                    'Elemento': ele_tag,
                    'Tipo': element_type,
                    'Nodo_I': node_i,
                    'Nodo_J': node_j,
                    'X_I': coord_i[0],
                    'Y_I': coord_i[1],
                    'Z_I': coord_i[2],
                    'X_J': coord_j[0],
                    'Y_J': coord_j[1],
                    'Z_J': coord_j[2],
                    'Longitud': length,
                    
                    # Fuerzas en nodo I (inicio)
                    'N_I': Ni,
                    'Vy_I': Vyi,
                    'Vz_I': Vzi,
                    'T_I': Ti,
                    'My_I': Myi,
                    'Mz_I': Mzi,
                    
                    # Fuerzas en centro
                    'N_Centro': Nc,
                    'Vy_Centro': Vyc,
                    'Vz_Centro': Vzc,
                    'T_Centro': Tc,
                    'My_Centro': Myc,
                    'Mz_Centro': Mzc,
                    
                    # Fuerzas en nodo J (final)
                    'N_J': Nj,
                    'Vy_J': Vyj,
                    'Vz_J': Vzj,
                    'T_J': Tj,
                    'My_J': Myj,
                    'Mz_J': Mzj
                })
                
            except Exception as e:
                print(f"    ⚠️ Error procesando elemento {ele_tag}: {e}")
                continue
        
        # Crear DataFrame y guardar
        if element_data:
            df = pd.DataFrame(element_data)
            
            # Ordenar por tipo de elemento y número
            df = df.sort_values(['Tipo', 'Elemento'])
            
            # Guardar CSV
            df.to_csv(filename, index=False, float_format='%.4f')
            
            print(f"✅ Archivo CSV detallado guardado: {filename}")
            print(f"   📊 {len(element_data)} elementos exportados")
            print(f"   🏗️ Tipos: {df['Tipo'].value_counts().to_dict()}")
            
            return df
        else:
            print("⚠️ No se pudieron procesar elementos")
            return None
            
    except Exception as e:
        print(f"❌ Error generando CSV detallado: {e}")
        return None

def generate_foundation_forces_csv(filename="foundation_forces.csv"):
    """
    Genera CSV con fuerzas en la base para diseño de zapatas
    """
    print(f"\n=== GENERANDO CSV DE FUERZAS EN CIMENTACIÓN ===")
    
    try:
        # Obtener todos los nodos
        node_tags = ops.getNodeTags()
        if not node_tags:
            print("⚠️ No hay nodos en el modelo")
            return None
        
        # Identificar nodos en la base (Z ≈ 0)
        base_nodes = []
        for node_tag in node_tags:
            coord = ops.nodeCoord(node_tag)
            if coord[2] < 0.01:  # Nodos en la base
                base_nodes.append(node_tag)
        
        if not base_nodes:
            print("⚠️ No se encontraron nodos en la base")
            return None
        
        # Obtener reacciones en la base
        foundation_data = []
        
        for node_tag in base_nodes:
            try:
                coord = ops.nodeCoord(node_tag)
                
                # Obtener reacciones (fuerzas en los apoyos)
                try:
                    # Asegurar que las reacciones están calculadas
                    try:
                        ops.reactions()
                    except:
                        pass  # Las reacciones pueden ya estar calculadas
                    
                    reactions = ops.nodeReaction(node_tag)
                    if reactions and len(reactions) >= 6:
                        Rx = reactions[0]  # Reacción en X
                        Ry = reactions[1]  # Reacción en Y
                        Rz = reactions[2]  # Reacción en Z (axial)
                        Mx = reactions[3]  # Momento en X
                        My = reactions[4]  # Momento en Y
                        Mz = reactions[5]  # Momento en Z
                    else:
                        print(f"    ⚠️ No se obtuvieron reacciones válidas para nodo {node_tag}")
                        Rx = Ry = Rz = Mx = My = Mz = 0
                except Exception as e:
                    print(f"    ⚠️ Error obteniendo reacciones del nodo {node_tag}: {e}")
                    Rx = Ry = Rz = Mx = My = Mz = 0
                
                # Buscar columnas que lleguen a este nodo
                connected_columns = []
                element_tags = ops.getEleTags()
                
                for ele_tag in element_tags:
                    try:
                        nodes = ops.eleNodes(ele_tag)
                        if node_tag in nodes:
                            # Verificar si es columna (elemento vertical)
                            other_node = nodes[1] if nodes[0] == node_tag else nodes[0]
                            other_coord = ops.nodeCoord(other_node)
                            
                            if other_coord[2] > coord[2] + 0.1:  # El otro nodo está arriba
                                connected_columns.append(ele_tag)
                    except:
                        continue
                
                foundation_data.append({
                    'Nodo': node_tag,
                    'X': coord[0],
                    'Y': coord[1],
                    'Z': coord[2],
                    'Columnas_Conectadas': ','.join(map(str, connected_columns)),
                    'Rx_kN': Rx,
                    'Ry_kN': Ry,
                    'Rz_kN': Rz,      # Carga axial (principal para zapatas)
                    'Mx_kNm': Mx,
                    'My_kNm': My,     # Momento principal para zapatas
                    'Mz_kNm': Mz,
                    'Resultante_kN': np.sqrt(Rx**2 + Ry**2 + Rz**2),
                    'Momento_Resultante_kNm': np.sqrt(Mx**2 + My**2 + Mz**2)
                })
                
            except Exception as e:
                print(f"    ⚠️ Error procesando nodo {node_tag}: {e}")
                continue
        
        # Crear DataFrame y guardar
        if foundation_data:
            df = pd.DataFrame(foundation_data)
            
            # Ordenar por posición
            df = df.sort_values(['Y', 'X'])
            
            # Guardar CSV
            df.to_csv(filename, index=False, float_format='%.4f')
            
            print(f"✅ Archivo CSV de cimentación guardado: {filename}")
            print(f"   📊 {len(foundation_data)} nodos de cimentación")
            print(f"   🏗️ Carga axial máxima: {df['Rz_kN'].max():.2f} kN")
            print(f"   🏗️ Momento máximo: {df['Momento_Resultante_kNm'].max():.2f} kN⋅m")
            
            return df
        else:
            print("⚠️ No se pudieron procesar nodos de cimentación")
            return None
            
    except Exception as e:
        print(f"❌ Error generando CSV de cimentación: {e}")
        return None

def generate_nodal_displacements_csv(filename="nodal_displacements_detailed.csv"):
    """
    Genera CSV detallado con desplazamientos nodales
    """
    print(f"\n=== GENERANDO CSV DETALLADO DE DESPLAZAMIENTOS ===")
    
    try:
        node_tags = ops.getNodeTags()
        if not node_tags:
            print("⚠️ No hay nodos en el modelo")
            return None
        
        displacement_data = []
        
        for node_tag in node_tags:
            try:
                coord = ops.nodeCoord(node_tag)
                
                # Obtener desplazamientos
                try:
                    disps = ops.nodeDisp(node_tag)
                    if disps and len(disps) >= 6:
                        ux = disps[0]  # Desplazamiento X
                        uy = disps[1]  # Desplazamiento Y
                        uz = disps[2]  # Desplazamiento Z
                        rx = disps[3]  # Rotación X
                        ry = disps[4]  # Rotación Y
                        rz = disps[5]  # Rotación Z
                    else:
                        print(f"    ⚠️ Desplazamientos insuficientes para nodo {node_tag}: {len(disps) if disps else 0} valores")
                        ux = uy = uz = rx = ry = rz = 0
                except Exception as e:
                    print(f"    ⚠️ Error obteniendo desplazamientos del nodo {node_tag}: {e}")
                    ux = uy = uz = rx = ry = rz = 0
                
                # Calcular desplazamiento resultante
                displacement_resultant = np.sqrt(ux**2 + uy**2 + uz**2)
                rotation_resultant = np.sqrt(rx**2 + ry**2 + rz**2)
                
                displacement_data.append({
                    'Nodo': node_tag,
                    'X': coord[0],
                    'Y': coord[1],
                    'Z': coord[2],
                    'Ux_m': ux,
                    'Uy_m': uy,
                    'Uz_m': uz,
                    'Rx_rad': rx,
                    'Ry_rad': ry,
                    'Rz_rad': rz,
                    'Despl_Resultante_m': displacement_resultant,
                    'Rot_Resultante_rad': rotation_resultant
                })
                
            except Exception as e:
                print(f"    ⚠️ Error procesando nodo {node_tag}: {e}")
                continue
        
        # Crear DataFrame y guardar
        if displacement_data:
            df = pd.DataFrame(displacement_data)
            
            # Ordenar por nivel y posición
            df = df.sort_values(['Z', 'Y', 'X'])
            
            # Guardar CSV
            df.to_csv(filename, index=False, float_format='%.6f')
            
            print(f"✅ Archivo CSV de desplazamientos guardado: {filename}")
            print(f"   📊 {len(displacement_data)} nodos exportados")
            print(f"   📏 Desplazamiento máximo: {df['Despl_Resultante_m'].max():.6f} m")
            
            return df
        else:
            print("⚠️ No se pudieron procesar desplazamientos")
            return None
            
    except Exception as e:
        print(f"❌ Error generando CSV de desplazamientos: {e}")
        return None

def generate_summary_report(filename="analysis_summary.txt"):
    """
    Genera un reporte resumen del análisis
    """
    print(f"\n=== GENERANDO REPORTE RESUMEN ===")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("REPORTE RESUMEN DE ANÁLISIS ESTRUCTURAL\n")
            f.write("="*60 + "\n")
            f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Sistema de unidades: Métrico (m, kN, s)\n\n")
            
            # Información del modelo
            try:
                node_tags = ops.getNodeTags()
                element_tags = ops.getEleTags()
                
                f.write("INFORMACIÓN DEL MODELO:\n")
                f.write("-"*30 + "\n")
                f.write(f"Total de nodos: {len(node_tags)}\n")
                f.write(f"Total de elementos: {len(element_tags)}\n")
                
                # Clasificar elementos
                columns = beams_x = beams_y = 0
                for ele_tag in element_tags:
                    try:
                        nodes = ops.eleNodes(ele_tag)
                        coord1 = np.array(ops.nodeCoord(nodes[0]))
                        coord2 = np.array(ops.nodeCoord(nodes[1]))
                        direction = coord2 - coord1
                        
                        if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                            columns += 1
                        elif abs(direction[0]) > abs(direction[1]):
                            beams_x += 1
                        else:
                            beams_y += 1
                    except:
                        continue
                
                f.write(f"  - Columnas: {columns}\n")
                f.write(f"  - Vigas X: {beams_x}\n")
                f.write(f"  - Vigas Y: {beams_y}\n\n")
                
                # Dimensiones de la estructura
                coords = [ops.nodeCoord(tag) for tag in node_tags]
                coords = np.array(coords)
                
                f.write("DIMENSIONES DE LA ESTRUCTURA:\n")
                f.write("-"*30 + "\n")
                f.write(f"Ancho (X): {coords[:, 0].max() - coords[:, 0].min():.2f} m\n")
                f.write(f"Largo (Y): {coords[:, 1].max() - coords[:, 1].min():.2f} m\n")
                f.write(f"Altura (Z): {coords[:, 2].max() - coords[:, 2].min():.2f} m\n\n")
                
            except Exception as e:
                f.write(f"Error obteniendo información del modelo: {e}\n\n")
            
            f.write("ARCHIVOS GENERADOS:\n")
            f.write("-"*30 + "\n")
            f.write("- detailed_elements.csv: Elementos con fuerzas detalladas\n")
            f.write("- foundation_forces.csv: Fuerzas en cimentación\n")
            f.write("- nodal_displacements_detailed.csv: Desplazamientos nodales\n")
            f.write("- nodes_table.csv: Tabla de nodos con coordenadas\n")
            f.write("- analysis_summary.txt: Este reporte\n\n")
            
            f.write("NOTAS:\n")
            f.write("-"*30 + "\n")
            f.write("- Use el archivo detailed_elements.csv para post-procesamiento\n")
            f.write("- Las fuerzas se reportan en tres puntos: inicio, centro, final\n")
            f.write("- Foundation_forces.csv contiene datos para diseño de zapatas\n")
            f.write("- nodes_table.csv contiene números y coordenadas de todos los nodos\n")
            f.write("- Coordenadas en metros, fuerzas en kN, momentos en kN⋅m\n")
        
        print(f"✅ Reporte resumen guardado: {filename}")
        
    except Exception as e:
        print(f"❌ Error generando reporte resumen: {e}")

def generate_nodes_table_csv(filename="nodes_table.csv"):
    """
    Genera CSV con tabla de nodos mostrando número y coordenadas
    """
    print(f"\n=== GENERANDO TABLA DE NODOS ===")
    
    try:
        # Obtener todos los nodos
        node_tags = ops.getNodeTags()
        if not node_tags:
            print("⚠️ No hay nodos en el modelo")
            return None
        
        # Lista para almacenar datos de nodos
        nodes_data = []
        
        for node_tag in node_tags:
            try:
                coord = ops.nodeCoord(node_tag)
                
                # Determinar tipo/nivel del nodo
                if coord[2] < 0.01:
                    node_type = "Base"
                    level = "Cimentación"
                else:
                    # Determinar nivel aproximado (asumiendo 3m por piso)
                    level_num = int(coord[2] / 3.0) + 1
                    if level_num == 1:
                        level = "Nivel 1"
                        node_type = "Estructura"
                    else:
                        level = f"Nivel {level_num}"
                        node_type = "Estructura"
                
                nodes_data.append({
                    'Nodo': node_tag,
                    'Tipo': node_type,
                    'Nivel': level,
                    'X_m': coord[0],
                    'Y_m': coord[1],
                    'Z_m': coord[2],
                    'X_cm': coord[0] * 100,
                    'Y_cm': coord[1] * 100,
                    'Z_cm': coord[2] * 100
                })
                
            except Exception as e:
                print(f"    ⚠️ Error procesando nodo {node_tag}: {e}")
                continue
        
        # Crear DataFrame y guardar
        if nodes_data:
            df = pd.DataFrame(nodes_data)
            
            # Ordenar por nivel (Z) y luego por posición (Y, X)
            df = df.sort_values(['Z_m', 'Y_m', 'X_m'])
            
            # Guardar CSV
            df.to_csv(filename, index=False, float_format='%.4f')
            
            print(f"✅ Tabla de nodos guardada: {filename}")
            print(f"   📊 {len(nodes_data)} nodos exportados")
            
            # Mostrar estadísticas por tipo
            type_counts = df['Tipo'].value_counts()
            level_counts = df['Nivel'].value_counts()
            print(f"   🏗️ Por tipo: {type_counts.to_dict()}")
            print(f"   📏 Por nivel: {level_counts.to_dict()}")
            
            return df
        else:
            print("⚠️ No se pudieron procesar nodos")
            return None
            
    except Exception as e:
        print(f"❌ Error generando tabla de nodos: {e}")
        return None

def generate_enhanced_results(column_elements=None, beam_x_elements=None, beam_y_elements=None, slab_elements=None):
    """
    Función principal para generar todos los archivos de resultados mejorados
    """
    print("\n" + "="*60)
    print("GENERANDO RESULTADOS MEJORADOS PARA POST-PROCESAMIENTO")
    print("="*60)
    
    # Generar CSVs detallados
    detailed_df = generate_detailed_element_csv()
    foundation_df = generate_foundation_forces_csv()
    displacements_df = generate_nodal_displacements_csv()
    nodes_df = generate_nodes_table_csv()
    
    # Generar reporte resumen
    generate_summary_report()
    
    print("\n✅ TODOS LOS ARCHIVOS DE RESULTADOS GENERADOS")
    print("📋 Use estos archivos para análisis detallado y post-procesamiento")
    
    return {
        'detailed_elements': detailed_df,
        'foundation_forces': foundation_df,
        'nodal_displacements': displacements_df,
        'nodes_table': nodes_df
    }