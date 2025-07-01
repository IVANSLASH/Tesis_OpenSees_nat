# load_combinations.py
# ============================================
# Sistema de combinaciones de cargas según ACI 318
# Permite seleccionar y aplicar diferentes combinaciones
# para obtener solicitaciones máximas para diseño
# ============================================

import openseespy.opensees as ops
import pandas as pd
import numpy as np
from copy import deepcopy

class ACI_LoadCombinations:
    """
    Clase para manejar combinaciones de cargas según ACI 318
    """
    
    def __init__(self):
        self.combinations = {
            # Combinaciones de resistencia (Strength Design)
            "U1": {
                "name": "1.4D",
                "description": "Solo carga muerta amplificada",
                "factors": {"D": 1.4, "L": 0.0, "Lr": 0.0, "S": 0.0, "W": 0.0, "E": 0.0}
            },
            "U2": {
                "name": "1.2D + 1.6L + 0.5(Lr o S)",
                "description": "Cargas gravitacionales principales",
                "factors": {"D": 1.2, "L": 1.6, "Lr": 0.5, "S": 0.5, "W": 0.0, "E": 0.0}
            },
            "U3": {
                "name": "1.2D + 1.6(Lr o S) + (L o 0.5W)",
                "description": "Cargas de cubierta principales",
                "factors": {"D": 1.2, "L": 1.0, "Lr": 1.6, "S": 1.6, "W": 0.5, "E": 0.0}
            },
            "U4": {
                "name": "1.2D + 1.0W + L + 0.5(Lr o S)",
                "description": "Carga de viento principal",
                "factors": {"D": 1.2, "L": 1.0, "Lr": 0.5, "S": 0.5, "W": 1.0, "E": 0.0}
            },
            "U5": {
                "name": "1.2D + 1.0E + L + 0.2S",
                "description": "Carga sísmica principal",
                "factors": {"D": 1.2, "L": 1.0, "Lr": 0.0, "S": 0.2, "W": 0.0, "E": 1.0}
            },
            "U6": {
                "name": "0.9D + 1.0W",
                "description": "Viento con carga muerta mínima",
                "factors": {"D": 0.9, "L": 0.0, "Lr": 0.0, "S": 0.0, "W": 1.0, "E": 0.0}
            },
            "U7": {
                "name": "0.9D + 1.0E",
                "description": "Sismo con carga muerta mínima",
                "factors": {"D": 0.9, "L": 0.0, "Lr": 0.0, "S": 0.0, "W": 0.0, "E": 1.0}
            }
        }
        
        # Combinaciones de servicio (Service Level)
        self.service_combinations = {
            "S1": {
                "name": "1.0D",
                "description": "Solo carga muerta",
                "factors": {"D": 1.0, "L": 0.0, "Lr": 0.0, "S": 0.0, "W": 0.0, "E": 0.0}
            },
            "S2": {
                "name": "1.0D + 1.0L",
                "description": "Cargas de servicio gravitacionales",
                "factors": {"D": 1.0, "L": 1.0, "Lr": 0.0, "S": 0.0, "W": 0.0, "E": 0.0}
            },
            "S3": {
                "name": "1.0D + 0.7W",
                "description": "Cargas de servicio con viento",
                "factors": {"D": 1.0, "L": 0.0, "Lr": 0.0, "S": 0.0, "W": 0.7, "E": 0.0}
            },
            "S4": {
                "name": "1.0D + 0.7E",
                "description": "Cargas de servicio con sismo",
                "factors": {"D": 1.0, "L": 0.0, "Lr": 0.0, "S": 0.0, "W": 0.0, "E": 0.7}
            }
        }

def get_user_load_combination_selection(interactive=True):
    """
    Permite al usuario seleccionar las combinaciones de cargas a analizar
    """
    if not interactive:
        # Selección por defecto: combinaciones principales
        return ["U1", "U2", "U5"]  # Muerta, gravitacional, sísmica
    
    aci = ACI_LoadCombinations()
    
    print("\n" + "="*70)
    print("SELECCIÓN DE COMBINACIONES DE CARGAS SEGÚN ACI 318")
    print("="*70)
    
    print("\n🔸 COMBINACIONES DE RESISTENCIA (Strength Design):")
    print("-" * 50)
    for key, combo in aci.combinations.items():
        print(f"{key}: {combo['name']}")
        print(f"    {combo['description']}")
        print()
    
    print("\n🔸 COMBINACIONES DE SERVICIO (Service Level):")
    print("-" * 50)
    for key, combo in aci.service_combinations.items():
        print(f"{key}: {combo['name']}")
        print(f"    {combo['description']}")
        print()
    
    print("💡 RECOMENDACIONES:")
    print("   • Para diseño estructural: Seleccione combinaciones U1, U2, U5")
    print("   • Para análisis completo: Seleccione todas las combinaciones U")
    print("   • Para verificación de servicio: Incluya combinaciones S")
    print()
    
    selected_combinations = []
    
    print("MÉTODOS DE SELECCIÓN:")
    print("1. Selección automática (recomendado para diseño)")
    print("2. Selección personalizada")
    print("3. Todas las combinaciones de resistencia")
    print("4. Análisis completo (resistencia + servicio)")
    
    while True:
        try:
            method = int(input("\nSeleccione el método (1-4): "))
            if method in [1, 2, 3, 4]:
                break
            else:
                print("Seleccione un número entre 1 y 4")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    if method == 1:
        # Selección automática para diseño
        selected_combinations = ["U1", "U2", "U5"]
        print(f"\n✅ Selección automática: {selected_combinations}")
        print("   • U1: Carga muerta amplificada")
        print("   • U2: Cargas gravitacionales principales") 
        print("   • U5: Carga sísmica principal")
        
    elif method == 2:
        # Selección personalizada
        print(f"\nCombinaciones disponibles:")
        all_combos = {**aci.combinations, **aci.service_combinations}
        for key, combo in all_combos.items():
            print(f"  {key}: {combo['name']}")
        
        print(f"\nIngrese las combinaciones separadas por comas (ej: U1,U2,U5):")
        selection = input("Combinaciones: ").strip().upper()
        
        for combo in selection.split(','):
            combo = combo.strip()
            if combo in all_combos:
                selected_combinations.append(combo)
            else:
                print(f"⚠️ Combinación '{combo}' no válida, omitida")
        
    elif method == 3:
        # Todas las combinaciones de resistencia
        selected_combinations = list(aci.combinations.keys())
        print(f"\n✅ Todas las combinaciones de resistencia: {selected_combinations}")
        
    elif method == 4:
        # Análisis completo
        selected_combinations = list(aci.combinations.keys()) + list(aci.service_combinations.keys())
        print(f"\n✅ Análisis completo: {selected_combinations}")
    
    if not selected_combinations:
        print("⚠️ No se seleccionaron combinaciones válidas, usando selección por defecto")
        selected_combinations = ["U1", "U2", "U5"]
    
    print(f"\n📋 COMBINACIONES SELECCIONADAS PARA ANÁLISIS:")
    all_combos = {**aci.combinations, **aci.service_combinations}
    for combo in selected_combinations:
        print(f"   • {combo}: {all_combos[combo]['name']}")
    
    return selected_combinations

def apply_load_combination(combination_id, base_loads):
    """
    Aplica una combinación de cargas específica
    
    Args:
        combination_id (str): ID de la combinación (ej: "U1", "U2")
        base_loads (dict): Cargas base por tipo {"D": dead_load, "L": live_load, etc.}
    
    Returns:
        dict: Factores aplicados para esta combinación
    """
    aci = ACI_LoadCombinations()
    all_combos = {**aci.combinations, **aci.service_combinations}
    
    if combination_id not in all_combos:
        raise ValueError(f"Combinación {combination_id} no encontrada")
    
    combination = all_combos[combination_id]
    factors = combination["factors"]
    
    print(f"\n🔄 Aplicando combinación {combination_id}: {combination['name']}")
    
    # Por ahora, simplificamos asumiendo que solo tenemos carga muerta (D) y viva (L)
    # En implementaciones futuras se pueden agregar W (viento), E (sismo), etc.
    
    applied_factors = {}
    for load_type, factor in factors.items():
        if factor > 0:
            applied_factors[load_type] = factor
            if load_type in ["D", "L"]:  # Solo mostrar los que realmente usamos
                print(f"   📊 Factor {load_type}: {factor}")
    
    return applied_factors

def analyze_load_combination(combination_id, run_analysis_func):
    """
    Ejecuta el análisis para una combinación específica de cargas
    
    Args:
        combination_id (str): ID de la combinación
        run_analysis_func (function): Función que ejecuta el análisis
    
    Returns:
        dict: Resultados del análisis para esta combinación
    """
    print(f"\n{'='*60}")
    print(f"ANÁLISIS PARA COMBINACIÓN: {combination_id}")
    print(f"{'='*60}")
    
    try:
        # Aplicar la combinación de cargas
        aci = ACI_LoadCombinations()
        all_combos = {**aci.combinations, **aci.service_combinations}
        combination = all_combos[combination_id]
        
        print(f"📋 {combination['name']}")
        print(f"📝 {combination['description']}")
        
        # Ejecutar análisis (la función debe manejar internamente la aplicación de factores)
        success = run_analysis_func()
        
        if success:
            print(f"✅ Análisis completado para {combination_id}")
            
            # Extraer resultados
            results = extract_analysis_results(combination_id)
            return results
        else:
            print(f"❌ Error en análisis para {combination_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error ejecutando combinación {combination_id}: {e}")
        return None

def extract_analysis_results(combination_id):
    """
    Extrae los resultados del análisis actual de OpenSeesPy
    """
    try:
        # Obtener elementos y sus fuerzas
        element_tags = ops.getEleTags()
        results = {
            'combination': combination_id,
            'elements': {}
        }
        
        for ele_tag in element_tags:
            try:
                forces = ops.eleForce(ele_tag)
                nodes = ops.eleNodes(ele_tag)
                
                if forces and len(forces) >= 12:
                    results['elements'][ele_tag] = {
                        'nodes': nodes,
                        'forces': {
                            'N1': forces[0], 'Vy1': forces[1], 'Vz1': forces[2],
                            'T1': forces[3], 'My1': forces[4], 'Mz1': forces[5],
                            'N2': forces[6], 'Vy2': forces[7], 'Vz2': forces[8],
                            'T2': forces[9], 'My2': forces[10], 'Mz2': forces[11]
                        }
                    }
            except:
                continue
        
        return results
        
    except Exception as e:
        print(f"⚠️ Error extrayendo resultados para {combination_id}: {e}")
        return None

def generate_maximum_demands_csv(all_combination_results, filename="maximum_demands_design.csv"):
    """
    Genera CSV con las solicitaciones máximas para diseño
    comparando todas las combinaciones de cargas
    """
    print(f"\n=== GENERANDO CSV DE SOLICITACIONES MÁXIMAS PARA DISEÑO ===")
    
    try:
        if not all_combination_results:
            print("⚠️ No hay resultados de combinaciones para procesar")
            return None
        
        # Estructura para almacenar máximos por elemento
        max_demands = {}
        
        # Procesar cada combinación
        for combo_id, results in all_combination_results.items():
            if results and 'elements' in results:
                print(f"   📊 Procesando combinación {combo_id}...")
                
                for ele_tag, ele_data in results['elements'].items():
                    if ele_tag not in max_demands:
                        # Inicializar elemento
                        max_demands[ele_tag] = {
                            'nodes': ele_data['nodes'],
                            'max_forces': {
                                'N_max': 0, 'N_max_combo': '',
                                'Vy_max': 0, 'Vy_max_combo': '',
                                'Vz_max': 0, 'Vz_max_combo': '',
                                'T_max': 0, 'T_max_combo': '',
                                'My_max': 0, 'My_max_combo': '',
                                'Mz_max': 0, 'Mz_max_combo': '',
                                # Valores mínimos (para comprensión/tensión)
                                'N_min': 0, 'N_min_combo': '',
                                'My_min': 0, 'My_min_combo': '',
                                'Mz_min': 0, 'Mz_min_combo': ''
                            }
                        }
                    
                    forces = ele_data['forces']
                    max_forces = max_demands[ele_tag]['max_forces']
                    
                    # Comparar fuerzas axiales (máximas y mínimas)
                    N_vals = [abs(forces['N1']), abs(forces['N2'])]
                    N_max_current = max(N_vals)
                    N_min_current = min(forces['N1'], forces['N2'])  # Para compresión
                    
                    if N_max_current > abs(max_forces['N_max']):
                        max_forces['N_max'] = N_max_current if forces['N1'] > forces['N2'] else forces['N2'] if abs(forces['N2']) > abs(forces['N1']) else forces['N1']
                        max_forces['N_max_combo'] = combo_id
                    
                    if N_min_current < max_forces['N_min']:
                        max_forces['N_min'] = N_min_current
                        max_forces['N_min_combo'] = combo_id
                    
                    # Comparar cortantes
                    Vy_vals = [abs(forces['Vy1']), abs(forces['Vy2'])]
                    Vy_max_current = max(Vy_vals)
                    if Vy_max_current > abs(max_forces['Vy_max']):
                        max_forces['Vy_max'] = forces['Vy1'] if abs(forces['Vy1']) > abs(forces['Vy2']) else forces['Vy2']
                        max_forces['Vy_max_combo'] = combo_id
                    
                    Vz_vals = [abs(forces['Vz1']), abs(forces['Vz2'])]
                    Vz_max_current = max(Vz_vals)
                    if Vz_max_current > abs(max_forces['Vz_max']):
                        max_forces['Vz_max'] = forces['Vz1'] if abs(forces['Vz1']) > abs(forces['Vz2']) else forces['Vz2']
                        max_forces['Vz_max_combo'] = combo_id
                    
                    # Comparar momentos (máximos y mínimos)
                    My_vals = [abs(forces['My1']), abs(forces['My2'])]
                    My_max_current = max(My_vals)
                    My_min_current = min(forces['My1'], forces['My2'])
                    
                    if My_max_current > abs(max_forces['My_max']):
                        max_forces['My_max'] = forces['My1'] if abs(forces['My1']) > abs(forces['My2']) else forces['My2']
                        max_forces['My_max_combo'] = combo_id
                    
                    if My_min_current < max_forces['My_min']:
                        max_forces['My_min'] = My_min_current
                        max_forces['My_min_combo'] = combo_id
                    
                    Mz_vals = [abs(forces['Mz1']), abs(forces['Mz2'])]
                    Mz_max_current = max(Mz_vals)
                    Mz_min_current = min(forces['Mz1'], forces['Mz2'])
                    
                    if Mz_max_current > abs(max_forces['Mz_max']):
                        max_forces['Mz_max'] = forces['Mz1'] if abs(forces['Mz1']) > abs(forces['Mz2']) else forces['Mz2']
                        max_forces['Mz_max_combo'] = combo_id
                    
                    if Mz_min_current < max_forces['Mz_min']:
                        max_forces['Mz_min'] = Mz_min_current
                        max_forces['Mz_min_combo'] = combo_id
                    
                    # Comparar torsión
                    T_vals = [abs(forces['T1']), abs(forces['T2'])]
                    T_max_current = max(T_vals)
                    if T_max_current > abs(max_forces['T_max']):
                        max_forces['T_max'] = forces['T1'] if abs(forces['T1']) > abs(forces['T2']) else forces['T2']
                        max_forces['T_max_combo'] = combo_id
        
        # Crear DataFrame para CSV
        design_data = []
        for ele_tag, data in max_demands.items():
            try:
                nodes = data['nodes']
                coord1 = ops.nodeCoord(nodes[0])
                coord2 = ops.nodeCoord(nodes[1])
                
                # Determinar tipo de elemento
                direction = np.array(coord2) - np.array(coord1)
                if abs(direction[2]) > max(abs(direction[0]), abs(direction[1])):
                    element_type = "Columna"
                elif abs(direction[0]) > abs(direction[1]):
                    element_type = "Viga_X"
                else:
                    element_type = "Viga_Y"
                
                max_forces = data['max_forces']
                
                design_data.append({
                    'Elemento': ele_tag,
                    'Tipo': element_type,
                    'Nodo_I': nodes[0],
                    'Nodo_J': nodes[1],
                    'X_I': coord1[0], 'Y_I': coord1[1], 'Z_I': coord1[2],
                    'X_J': coord2[0], 'Y_J': coord2[1], 'Z_J': coord2[2],
                    
                    # Solicitaciones máximas para diseño
                    'N_max_kN': max_forces['N_max'],
                    'N_max_Combo': max_forces['N_max_combo'],
                    'N_min_kN': max_forces['N_min'],  # Para compresión
                    'N_min_Combo': max_forces['N_min_combo'],
                    
                    'Vy_max_kN': max_forces['Vy_max'],
                    'Vy_max_Combo': max_forces['Vy_max_combo'],
                    'Vz_max_kN': max_forces['Vz_max'],
                    'Vz_max_Combo': max_forces['Vz_max_combo'],
                    
                    'My_max_kNm': max_forces['My_max'],
                    'My_max_Combo': max_forces['My_max_combo'],
                    'My_min_kNm': max_forces['My_min'],
                    'My_min_Combo': max_forces['My_min_combo'],
                    
                    'Mz_max_kNm': max_forces['Mz_max'],
                    'Mz_max_Combo': max_forces['Mz_max_combo'],
                    'Mz_min_kNm': max_forces['Mz_min'],
                    'Mz_min_Combo': max_forces['Mz_min_combo'],
                    
                    'T_max_kNm': max_forces['T_max'],
                    'T_max_Combo': max_forces['T_max_combo']
                })
                
            except Exception as e:
                print(f"    ⚠️ Error procesando elemento {ele_tag}: {e}")
                continue
        
        if design_data:
            df = pd.DataFrame(design_data)
            
            # Ordenar por tipo y número de elemento
            df = df.sort_values(['Tipo', 'Elemento'])
            
            # Guardar CSV
            df.to_csv(filename, index=False, float_format='%.4f')
            
            print(f"✅ Archivo de solicitaciones máximas guardado: {filename}")
            print(f"   📊 {len(design_data)} elementos procesados")
            
            # Mostrar estadísticas
            type_counts = df['Tipo'].value_counts()
            print(f"   🏗️ Elementos por tipo: {type_counts.to_dict()}")
            
            # Mostrar combinaciones más críticas
            combo_counts = {}
            for col in df.columns:
                if col.endswith('_Combo'):
                    for combo in df[col].values:
                        if combo:
                            combo_counts[combo] = combo_counts.get(combo, 0) + 1
            
            print(f"   🔥 Combinaciones más críticas: {dict(sorted(combo_counts.items(), key=lambda x: x[1], reverse=True)[:3])}")
            
            return df
        else:
            print("⚠️ No se pudieron procesar elementos para el CSV de diseño")
            return None
            
    except Exception as e:
        print(f"❌ Error generando CSV de solicitaciones máximas: {e}")
        return None