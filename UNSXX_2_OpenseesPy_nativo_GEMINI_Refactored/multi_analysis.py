# multi_analysis.py
# ============================================
# Sistema de análisis múltiple con combinaciones de cargas ACI
# Ejecuta análisis para múltiples combinaciones y genera
# resultados comparativos para diseño estructural
# ============================================

import openseespy.opensees as ops
from load_combinations import *
from loads import apply_load_combination_factors
from analysis import run_analysis
from results_enhanced import generate_enhanced_results
from load_combinations import generate_maximum_demands_csv
import pandas as pd
import numpy as np
import copy

def run_multi_load_combination_analysis(geometry_data, load_intensities, beam_elements_x, 
                                       beam_elements_y, selected_combinations, interactive=True):
    """
    Ejecuta análisis para múltiples combinaciones de cargas
    
    Args:
        geometry_data (dict): Datos de geometría del edificio
        load_intensities (dict): Intensidades de carga base
        beam_elements_x (list): Lista de elementos viga en X
        beam_elements_y (list): Lista de elementos viga en Y
        selected_combinations (list): Lista de combinaciones seleccionadas
        interactive (bool): Mostrar información detallada
    
    Returns:
        dict: Resultados de todas las combinaciones
    """
    print("\n" + "="*80)
    print("ANÁLISIS MÚLTIPLE CON COMBINACIONES DE CARGAS ACI 318")
    print("="*80)
    
    aci = ACI_LoadCombinations()
    all_combos = {**aci.combinations, **aci.service_combinations}
    all_results = {}
    successful_analyses = 0
    
    print(f"\n📋 COMBINACIONES A ANALIZAR: {len(selected_combinations)}")
    for combo in selected_combinations:
        if combo in all_combos:
            print(f"   • {combo}: {all_combos[combo]['name']}")
        else:
            print(f"   ⚠️ {combo}: Combinación no encontrada")
    
    # Ejecutar análisis para cada combinación
    for i, combination_id in enumerate(selected_combinations, 1):
        print(f"\n{'='*60}")
        print(f"ANÁLISIS {i}/{len(selected_combinations)}: {combination_id}")
        print(f"{'='*60}")
        
        if combination_id not in all_combos:
            print(f"❌ Combinación {combination_id} no válida, omitiendo...")
            continue
        
        combination = all_combos[combination_id]
        factors = combination["factors"]
        
        print(f"📋 {combination['name']}")
        print(f"📝 {combination['description']}")
        print(f"🔢 Factores: {factors}")
        
        try:
            # Limpiar modelo para nueva combinación
            print("\n  🧹 Limpiando cargas anteriores...")
            ops.wipeAnalysis()
            ops.remove('loadPattern', 1)
            ops.remove('loadPattern', 2)
            try:
                ops.remove('loadPattern', 3)
            except:
                pass
            
            # Aplicar cargas con factores de esta combinación
            dead_factor = factors.get("D", 0.0)
            live_factor = factors.get("L", 0.0)
            
            print(f"\n  🔄 Aplicando factores de carga...")
            print(f"     Factor muerta (D): {dead_factor}")
            print(f"     Factor viva (L): {live_factor}")
            
            apply_load_combination_factors(
                geometry_data, load_intensities, beam_elements_x, beam_elements_y,
                dead_factor, live_factor, combination['name']
            )
            
            # Ejecutar análisis
            print(f"\n  ⚙️ Ejecutando análisis estructural...")
            analysis_success = run_analysis()
            
            if analysis_success:
                print(f"  ✅ Análisis exitoso para {combination_id}")
                
                # Extraer resultados
                results = extract_analysis_results(combination_id)
                if results:
                    all_results[combination_id] = results
                    successful_analyses += 1
                    print(f"  📊 Resultados extraídos: {len(results.get('elements', {}))} elementos")
                else:
                    print(f"  ⚠️ Error extrayendo resultados para {combination_id}")
            else:
                print(f"  ❌ Error en análisis para {combination_id}")
                
        except Exception as e:
            print(f"  💥 Error ejecutando combinación {combination_id}: {e}")
            continue
    
    # Resumen de análisis completados
    print(f"\n{'='*60}")
    print(f"RESUMEN DE ANÁLISIS MÚLTIPLE")
    print(f"{'='*60}")
    print(f"✅ Análisis exitosos: {successful_analyses}/{len(selected_combinations)}")
    print(f"📊 Combinaciones con resultados: {list(all_results.keys())}")
    
    if successful_analyses == 0:
        print("❌ No se completó ningún análisis exitosamente")
        return None
    
    return all_results

def generate_comparison_results(all_combination_results, geometry_data, interactive=True):
    """
    Genera archivos de resultados comparativos y de diseño
    
    Args:
        all_combination_results (dict): Resultados de todas las combinaciones
        geometry_data (dict): Datos de geometría 
        interactive (bool): Mostrar información detallada
    
    Returns:
        dict: DataFrames generados
    """
    print(f"\n{'='*60}")
    print("GENERANDO RESULTADOS COMPARATIVOS Y DE DISEÑO")
    print(f"{'='*60}")
    
    if not all_combination_results:
        print("⚠️ No hay resultados para procesar")
        return None
    
    generated_files = {}
    
    try:
        # 1. Generar CSV de solicitaciones máximas para diseño
        print(f"\n🎯 Generando solicitaciones máximas para diseño...")
        max_demands_df = generate_maximum_demands_csv(
            all_combination_results, 
            "maximum_demands_design.csv"
        )
        if max_demands_df is not None:
            generated_files['maximum_demands'] = max_demands_df
        
        # 2. Generar CSV comparativo de todas las combinaciones
        print(f"\n📊 Generando comparación de todas las combinaciones...")
        comparison_df = generate_combination_comparison_csv(
            all_combination_results,
            "load_combinations_comparison.csv"
        )
        if comparison_df is not None:
            generated_files['combinations_comparison'] = comparison_df
        
        # 3. Generar resumen estadístico
        print(f"\n📈 Generando resumen estadístico...")
        stats_df = generate_statistics_summary_csv(
            all_combination_results,
            "analysis_statistics.csv"
        )
        if stats_df is not None:
            generated_files['statistics'] = stats_df
        
        # 4. Generar archivo de resultados de la última combinación
        print(f"\n💾 Generando resultados detallados de la última combinación...")
        last_combo = list(all_combination_results.keys())[-1]
        
        # Ejecutar generación de resultados estándar para la última combinación
        try:
            standard_results = generate_enhanced_results()
            if standard_results:
                print(f"  ✅ Archivos estándar generados para {last_combo}")
        except Exception as e:
            print(f"  ⚠️ Error generando archivos estándar: {e}")
        
        print(f"\n✅ ARCHIVOS DE ANÁLISIS MÚLTIPLE GENERADOS:")
        print(f"   📊 maximum_demands_design.csv - Solicitaciones máximas para diseño")
        print(f"   📋 load_combinations_comparison.csv - Comparación de combinaciones")
        print(f"   📈 analysis_statistics.csv - Estadísticas del análisis")
        print(f"   💾 Archivos estándar (detailed_elements.csv, etc.)")
        
        return generated_files
        
    except Exception as e:
        print(f"❌ Error generando resultados comparativos: {e}")
        return None

def generate_combination_comparison_csv(all_combination_results, filename="load_combinations_comparison.csv"):
    """
    Genera CSV con comparación detallada de todas las combinaciones
    """
    print(f"   📊 Creando comparación detallada...")
    
    try:
        comparison_data = []
        
        for combo_id, results in all_combination_results.items():
            if results and 'elements' in results:
                for ele_tag, ele_data in results['elements'].items():
                    try:
                        nodes = ele_data['nodes']
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
                        
                        forces = ele_data['forces']
                        
                        comparison_data.append({
                            'Combinacion': combo_id,
                            'Elemento': ele_tag,
                            'Tipo': element_type,
                            'Nodo_I': nodes[0],
                            'Nodo_J': nodes[1],
                            'N1_kN': forces['N1'],
                            'N2_kN': forces['N2'],
                            'Vy1_kN': forces['Vy1'],
                            'Vy2_kN': forces['Vy2'],
                            'Vz1_kN': forces['Vz1'],
                            'Vz2_kN': forces['Vz2'],
                            'My1_kNm': forces['My1'],
                            'My2_kNm': forces['My2'],
                            'Mz1_kNm': forces['Mz1'],
                            'Mz2_kNm': forces['Mz2'],
                            'T1_kNm': forces['T1'],
                            'T2_kNm': forces['T2'],
                            'N_max_kN': max(abs(forces['N1']), abs(forces['N2'])),
                            'V_max_kN': max(abs(forces['Vy1']), abs(forces['Vy2']), 
                                          abs(forces['Vz1']), abs(forces['Vz2'])),
                            'M_max_kNm': max(abs(forces['My1']), abs(forces['My2']), 
                                           abs(forces['Mz1']), abs(forces['Mz2']))
                        })
                        
                    except Exception as e:
                        print(f"      ⚠️ Error procesando elemento {ele_tag} en {combo_id}: {e}")
                        continue
        
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            
            # Ordenar por combinación, tipo y elemento
            df = df.sort_values(['Combinacion', 'Tipo', 'Elemento'])
            
            # Guardar CSV
            df.to_csv(filename, index=False, float_format='%.4f')
            
            print(f"   ✅ Comparación guardada: {filename}")
            print(f"   📊 {len(comparison_data)} registros de combinación-elemento")
            
            return df
        else:
            print(f"   ⚠️ No se pudieron procesar datos para comparación")
            return None
            
    except Exception as e:
        print(f"   ❌ Error generando comparación: {e}")
        return None

def generate_statistics_summary_csv(all_combination_results, filename="analysis_statistics.csv"):
    """
    Genera CSV con estadísticas resumidas del análisis
    """
    print(f"   📈 Creando resumen estadístico...")
    
    try:
        stats_data = []
        
        for combo_id, results in all_combination_results.items():
            if results and 'elements' in results:
                # Recopilar todas las fuerzas
                all_N = []
                all_V = []
                all_M = []
                
                for ele_tag, ele_data in results['elements'].items():
                    forces = ele_data['forces']
                    
                    all_N.extend([abs(forces['N1']), abs(forces['N2'])])
                    all_V.extend([abs(forces['Vy1']), abs(forces['Vy2']), 
                                 abs(forces['Vz1']), abs(forces['Vz2'])])
                    all_M.extend([abs(forces['My1']), abs(forces['My2']), 
                                 abs(forces['Mz1']), abs(forces['Mz2'])])
                
                if all_N and all_V and all_M:
                    stats_data.append({
                        'Combinacion': combo_id,
                        'Elementos_Total': len(results['elements']),
                        'N_max_kN': max(all_N),
                        'N_min_kN': min(all_N),
                        'N_promedio_kN': sum(all_N) / len(all_N),
                        'V_max_kN': max(all_V),
                        'V_min_kN': min(all_V),
                        'V_promedio_kN': sum(all_V) / len(all_V),
                        'M_max_kNm': max(all_M),
                        'M_min_kNm': min(all_M),
                        'M_promedio_kNm': sum(all_M) / len(all_M)
                    })
        
        if stats_data:
            df = pd.DataFrame(stats_data)
            
            # Ordenar por fuerza máxima
            df = df.sort_values('N_max_kN', ascending=False)
            
            # Guardar CSV
            df.to_csv(filename, index=False, float_format='%.4f')
            
            print(f"   ✅ Estadísticas guardadas: {filename}")
            print(f"   📊 {len(stats_data)} combinaciones analizadas")
            
            return df
        else:
            print(f"   ⚠️ No se pudieron calcular estadísticas")
            return None
            
    except Exception as e:
        print(f"   ❌ Error generando estadísticas: {e}")
        return None

def run_complete_load_combination_analysis(geometry_data, load_intensities, beam_elements_x, 
                                          beam_elements_y, interactive=True):
    """
    Función principal para ejecutar análisis completo con combinaciones de cargas
    
    Returns:
        dict: Todos los resultados generados
    """
    print("\n" + "🚀" + "="*78 + "🚀")
    print("ANÁLISIS ESTRUCTURAL CON COMBINACIONES DE CARGAS ACI 318")
    print("🚀" + "="*78 + "🚀")
    
    try:
        # 1. Selección de combinaciones
        print("\n1️⃣ SELECCIÓN DE COMBINACIONES DE CARGAS")
        selected_combinations = get_user_load_combination_selection(interactive)
        
        if not selected_combinations:
            print("❌ No se seleccionaron combinaciones válidas")
            return None
        
        # 2. Análisis múltiple
        print("\n2️⃣ ANÁLISIS MÚLTIPLE")
        all_results = run_multi_load_combination_analysis(
            geometry_data, load_intensities, beam_elements_x, beam_elements_y,
            selected_combinations, interactive
        )
        
        if not all_results:
            print("❌ No se obtuvieron resultados del análisis múltiple")
            return None
        
        # 3. Generación de resultados comparativos
        print("\n3️⃣ GENERACIÓN DE RESULTADOS")
        comparison_results = generate_comparison_results(all_results, geometry_data, interactive)
        
        # 4. Resumen final
        print(f"\n{'🎉' + '='*60 + '🎉'}")
        print("ANÁLISIS CON COMBINACIONES DE CARGAS COMPLETADO")
        print(f"{'🎉' + '='*60 + '🎉'}")
        
        print(f"\n📋 RESUMEN FINAL:")
        print(f"   • Combinaciones analizadas: {len(all_results)}")
        print(f"   • Combinaciones: {list(all_results.keys())}")
        print(f"   • Archivos generados: 7+ archivos CSV y de análisis")
        
        print(f"\n💡 ARCHIVOS PRINCIPALES PARA DISEÑO:")
        print(f"   🎯 maximum_demands_design.csv - Solicitaciones máximas")
        print(f"   📊 load_combinations_comparison.csv - Comparación detallada")
        print(f"   📈 analysis_statistics.csv - Estadísticas por combinación")
        print(f"   💾 foundation_forces.csv - Fuerzas para zapatas")
        
        return {
            'combination_results': all_results,
            'comparison_results': comparison_results,
            'selected_combinations': selected_combinations
        }
        
    except Exception as e:
        print(f"❌ Error en análisis completo: {e}")
        return None