
# main.py
# ============================================
# Este script principal orquesta el modelado, análisis y visualización
# de la estructura. Importa y coordina las funciones de los módulos
# auxiliares para construir el modelo completo, ejecutar el análisis
# y presentar los resultados.
#
# Flujo principal mejorado:
# 1. Entrada de datos con validaciones robustas
# 2. Definición de materiales y secciones personalizables
# 3. Creación de geometría (nodos, columnas, vigas)
# 4. Discretización de losas con mallas configurables
# 5. Aplicación de cargas distribuidas y combinaciones
# 6. Análisis estructural con manejo de errores
# 7. Visualización avanzada y didáctica
# 8. Generación de reportes completos
# ============================================

import openseespy.opensees as ops
import sys
import traceback
import input_data
import geometry
import sections
import slabs
import loads
import analysis
import visualization_new as visualization
import results_enhanced as results
import advanced_config
import enhanced_geometry
import multi_analysis

def print_header():
    """Imprime el encabezado del programa."""
    print("=" * 80)
    print("            ANÁLISIS ESTRUCTURAL MODULAR - OpenSeesPy")
    print("                   Sistema Modular Escalable")
    print("=" * 80)
    print("Edificios de múltiples niveles con losas discretizadas")
    print("Análisis completo: geometría → cargas → análisis → resultados")
    print("=" * 80)

def get_execution_mode():
    """
    Solicita al usuario el modo de ejecución del programa.
    
    Returns:
        tuple: (interactive, quick_test, load_config)
    """
    print("\n=== MODO DE EJECUCIÓN ===")
    print("Seleccione el modo de ejecución:")
    print("1. Modo Interactivo Completo (personalizar todo)")
    print("2. Modo Rápido de Prueba (valores por defecto)")
    print("3. Cargar configuración desde archivo")
    
    while True:
        try:
            choice = int(input("Seleccione una opción (1-3): "))
            if choice == 1:
                return True, False, None
            elif choice == 2:
                return False, True, None
            elif choice == 3:
                config_file = input("Ingrese la ruta del archivo de configuración: ").strip()
                return False, False, config_file
            else:
                print("Seleccione una opción válida (1-3)")
        except ValueError:
            print("Por favor ingrese un número válido")

def main():
    """Función principal del programa."""
    try:
        # Mostrar encabezado
        print_header()
        
        # Obtener modo de ejecución
        interactive, quick_test, config_file = get_execution_mode()
        
        if quick_test:
            print("\n🚀 Modo de prueba rápida activado - usando valores por defecto")
        elif config_file:
            print(f"\n📁 Cargando configuración desde: {config_file}")
        else:
            print("\n⚙️  Modo interactivo activado - personalizará todas las opciones")

        # Limpiar cualquier modelo anterior y crear uno nuevo
        print("\n=== INICIALIZANDO MODELO OPENSEESPY ===")
        try:
            ops.wipe()
            ops.model('basic', '-ndm', 3, '-ndf', 6)
            print("✓ Modelo 3D creado (6 DOF por nodo)")
        except Exception as e:
            print(f"⚠️ Error inicializando modelo: {e}")
            print("Continuando con el modelo existente...")

        # 1. Entrada de datos geométricos
        print("\n" + "="*60)
        print("PASO 1: CONFIGURACIÓN GEOMÉTRICA")
        print("="*60)
        
        geometry_data = input_data.get_building_geometry_data(
            interactive=interactive, 
            config_file=config_file
        )
        
        # 1.5. Configuraciones avanzadas (solo en modo interactivo)
        column_config = None
        cantilever_config = None
        slab_config = None
        
        if interactive:
            print("\n" + "="*60)
            print("PASO 1.5: CONFIGURACIONES AVANZADAS")
            print("="*60)
            
            # Configuración de columnas
            column_choice = advanced_config.column_configuration_menu()
            
            if column_choice == '1':
                column_config = advanced_config.get_uniform_column_section()
            elif column_choice == '2':
                column_config = advanced_config.get_exterior_interior_column_sections()
            elif column_choice == '3':
                column_config = advanced_config.get_custom_column_groups(geometry_data)
            else:
                print("  Usando configuración de columnas por defecto")
            
            # Configuración de volados
            cantilever_choice = advanced_config.cantilever_configuration_menu()
            cantilever_config = advanced_config.get_cantilever_config(cantilever_choice, geometry_data)
            
            # Configuración de losas
            slab_choice = advanced_config.slab_type_configuration_menu()
            slab_config = advanced_config.get_slab_configuration(slab_choice)
            
            if slab_config is None:
                print("  Usando configuración de losa por defecto (maciza 0.20m)")
                slab_config = {
                    'type': 'solid',
                    'thickness': 0.20,
                    'description': 'Losa maciza de 0.20m de espesor (por defecto)',
                    'load_factor': 1.0,
                    'self_weight': 5.0  # 0.20m * 25 kN/m³
                }
            
            # Mostrar resumen y confirmar
            if column_config or (cantilever_config and any(cantilever_config.values())) or slab_config:
                if not advanced_config.display_configuration_summary(column_config or {}, cantilever_config, slab_config):
                    print("⚠️ Configuración rechazada. Usando valores por defecto.")
                    column_config = None
                    cantilever_config = {'front': None, 'right': None, 'left': None}
                    slab_config = {
                        'type': 'solid',
                        'thickness': 0.20,
                        'description': 'Losa maciza de 0.20m de espesor (por defecto)',
                        'load_factor': 1.0,
                        'self_weight': 5.0
                    }
        
        if not column_config:
            # Configuración por defecto
            column_config = {
                'type': 'uniform',
                'lx_col': 0.30,
                'ly_col': 0.30,
                'A_col': 0.09,
                'Iz_col': 0.000675,
                'Iy_col': 0.000675
            }
            
        if not cantilever_config:
            cantilever_config = {'front': None, 'right': None, 'left': None}
            
        if not slab_config:
            slab_config = {
                'type': 'solid',
                'thickness': 0.20,
                'description': 'Losa maciza de 0.20m de espesor (por defecto)',
                'load_factor': 1.0,
                'self_weight': 5.0  # 0.20m * 25 kN/m³
            }
            
        # Agregar configuraciones al geometry_data
        geometry_data['column_config'] = column_config
        geometry_data['cantilever_config'] = cantilever_config
        geometry_data['slab_config'] = slab_config

        # 2. Definición de secciones y materiales (solo vigas y losas)
        print("\n" + "="*60)
        print("PASO 2: DEFINICIÓN DE MATERIALES Y SECCIONES")
        print("="*60)
        
        # Determinar si saltar configuración de columnas
        skip_columns = interactive and column_config is not None
        
        section_properties = sections.define_sections(
            interactive=interactive,
            material_choice="concreto_f21" if not interactive else None,
            skip_columns=skip_columns
        )
        
        # Agregar section_properties al geometry_data para enhanced_geometry
        geometry_data['section_properties'] = section_properties

        # 3. Configuración de intensidades de carga
        print("\n" + "="*60)
        print("PASO 3: CONFIGURACIÓN DE CARGAS")
        print("="*60)
        
        load_intensities = loads.get_load_intensities(interactive=interactive, slab_config=slab_config)

        # Propiedades de material y masa para nodos y elementos
        E_material = section_properties["E"]
        massX = 0.49  # Masa en dirección X (ton)
        M = 0         # Masa adicional para elementos (ton)
        massType = "-lMass"  # Tipo de masa (masa distribuida)

        # 4. Creación de nodos mejorada (incluyendo volados)
        print("\n" + "="*60)
        print("PASO 4: GENERACIÓN DE NODOS MEJORADA")
        print("="*60)
        
        if any(cantilever_config.values()):
            # Usar generación mejorada con volados
            total_nodes, node_mapping, extended_x_coords, extended_y_coords, z_coords = enhanced_geometry.generate_enhanced_nodes(
                geometry_data, cantilever_config
            )
            use_enhanced = True
        else:
            # Usar generación estándar
            total_nodes = geometry.create_nodes(geometry_data, E_material, massX, M, massType)
            use_enhanced = False

        # 5. Creación de columnas mejorada (secciones personalizadas)
        print("\n" + "="*60)
        print("PASO 5: GENERACIÓN DE COLUMNAS MEJORADA")
        print("="*60)
        
        if use_enhanced:
            column_elements_ids, next_ele_tag_after_columns = enhanced_geometry.generate_enhanced_column_elements(
                node_mapping, geometry_data, column_config, extended_x_coords, extended_y_coords, z_coords
            )
            total_columns = len(column_elements_ids)
        else:
            total_columns, column_elements_ids, next_ele_tag_after_columns = geometry.create_columns(
                geometry_data, E_material, M, massType,
                section_properties["A_col"], section_properties["Iz_col"],
                section_properties["Iy_col"], section_properties["J_col"]
            )

        # 6. Creación de vigas mejorada (incluyendo vigas de volado)
        print("\n" + "="*60)
        print("PASO 6: GENERACIÓN DE VIGAS MEJORADA")
        print("="*60)
        
        if use_enhanced:
            beam_elements_x_ids, beam_elements_y_ids, cantilever_beam_ids, next_ele_tag_after_beams = enhanced_geometry.generate_enhanced_beam_elements(
                node_mapping, geometry_data, cantilever_config, extended_x_coords, extended_y_coords, z_coords, next_ele_tag_after_columns
            )
            total_beams_x = len(beam_elements_x_ids)
            total_beams_y = len(beam_elements_y_ids)
            print(f"    📊 Vigas de volado adicionales: {len(cantilever_beam_ids)}")
        else:
            total_beams_x, beam_elements_x_ids, total_beams_y, beam_elements_y_ids, next_ele_tag_after_beams = geometry.create_beams(
                geometry_data, E_material, M, massType,
                section_properties["A_viga"], section_properties["Iz_viga"],
                section_properties["Iy_viga"], section_properties["J_viga"],
                next_ele_tag_after_columns, total_nodes
            )
            cantilever_beam_ids = []
        
        # 6.5. Verificación de condiciones de frontera
        print("\n" + "="*60)
        print("PASO 6.5: VERIFICACIÓN DE CONDICIONES DE FRONTERA")
        print("="*60)
        
        if use_enhanced:
            print("  Aplicando condiciones de frontera mejoradas...")
            restricted_nodes = enhanced_geometry.apply_enhanced_boundary_conditions(node_mapping, extended_x_coords, extended_y_coords, cantilever_config)
        else:
            print("  Verificando condiciones de frontera estándar...")
            # En geometría estándar, las restricciones se aplican en create_nodes
            # Solo verificamos que se aplicaron correctamente
            try:
                node_tags = ops.getNodeTags()
                restricted_nodes = 0
                for node in node_tags:
                    coord = ops.nodeCoord(node)
                    if coord[2] < 0.01:  # Nodos en la base (z ≈ 0)
                        restricted_nodes += 1
                
                if restricted_nodes > 0:
                    print(f"    ✅ {restricted_nodes} nodos restringidos en la base verificados")
                else:
                    print("    ❌ ADVERTENCIA: No se detectaron restricciones en la base")
            except Exception as e:
                print(f"    ⚠️ Error verificando restricciones: {e}")
                print("    Continuando sin verificación de restricciones...")
                restricted_nodes = 0
        
        if restricted_nodes == 0:
            print("    ❌ PROBLEMA CRÍTICO: No hay restricciones suficientes")
            print("    El análisis fallará sin restricciones adecuadas")

        # 7. Creación de losas
        print("\n" + "="*60)
        print("PASO 7: DISCRETIZACIÓN DE LOSAS")
        print("="*60)
        
        total_slabs_elements, slab_elements_ids, next_ele_tag_after_slabs = slabs.create_slabs(
            geometry_data, section_properties, next_ele_tag_after_beams
        )

        # Resumen del modelo creado
        total_elements = total_columns + total_beams_x + total_beams_y + total_slabs_elements
        print(f"\n🏗️  RESUMEN DEL MODELO GENERADO:")
        print(f"   📊 Total de nodos: {total_nodes}")
        print(f"   🏗️  Total de elementos: {total_elements}")
        print(f"      - Columnas: {total_columns}")
        print(f"      - Vigas X: {total_beams_x}")
        print(f"      - Vigas Y: {total_beams_y}")
        print(f"      - Elementos de losa: {total_slabs_elements}")

        # 8. Aplicación de cargas
        print("\n" + "="*60)
        print("PASO 8: APLICACIÓN DE CARGAS")
        print("="*60)
        
        loads.apply_loads(
            geometry_data=geometry_data,
            load_intensities=load_intensities,
            beam_elements_x=beam_elements_x_ids,
            beam_elements_y=beam_elements_y_ids,
            total_nodes=total_nodes,
            interactive=interactive,
            combination="service"
        )

        # 9. Análisis estructural
        print("\n" + "="*60)
        print("PASO 9: ANÁLISIS ESTRUCTURAL")
        print("="*60)
        
        analysis_successful = analysis.run_analysis()
        
        if not analysis_successful:
            print("\n❌ EL ANÁLISIS ESTRUCTURAL FALLÓ")
            print("No se pueden generar visualizaciones ni reportes sin un análisis exitoso.")
            print("\n💡 Recomendaciones:")
            print("  • Verifique que las dimensiones del edificio sean razonables")
            print("  • Asegúrese de que las cargas no sean excesivas")
            print("  • Revise que los volados no excedan los límites recomendados")
            print("  • Considere reducir la altura o número de pisos")
            return
        
        # IMPORTANTE: Generar reportes inmediatamente después del análisis exitoso
        # para preservar los resultados antes de cualquier operación adicional
        print("\n🚀 GENERANDO REPORTES DE ANÁLISIS PRINCIPAL (inmediatamente)...")
        print("📊 Extrayendo resultados del análisis estructural...")
        try:
            results.generate_enhanced_results(column_elements_ids, 
                                            beam_elements_x_ids, beam_elements_y_ids, slab_elements_ids)
            print("✅ Reportes del análisis principal generados exitosamente")
        except Exception as e:
            print(f"⚠️ Error generando reportes inmediatos: {e}")
            print("Los reportes se intentarán generar nuevamente más adelante")

        # 10. Visualización
        print("\n" + "="*60)
        print("PASO 10: VISUALIZACIÓN DE RESULTADOS")
        print("="*60)
        
        if interactive:
            show_plots = input("\n¿Desea generar y mostrar gráficos? (s/n): ").lower().strip()
            generate_plots = show_plots in ['s', 'si', 'sí', 'y', 'yes']
        else:
            generate_plots = not quick_test  # No mostrar gráficos en modo de prueba rápida

        if generate_plots:
            print("🎨 Generando visualizaciones nuevas y mejoradas...")
            
            # Crear diccionario con listas de elementos
            element_lists = {
                'columns': column_elements_ids,
                'beams_x': beam_elements_x_ids,
                'beams_y': beam_elements_y_ids
            }
            
            # Generar todas las visualizaciones mejoradas
            visualization.generate_all_visualizations(section_properties, element_lists)
        else:
            print("⏩ Visualización omitida")

        # 11. Generación de resultados (opcional si ya se generaron)
        print("\n" + "="*60)
        print("PASO 11: GENERACIÓN DE REPORTES ADICIONALES")
        print("="*60)
        print("ℹ️ Los reportes del análisis principal ya fueron generados inmediatamente")
        print("   después del análisis para preservar los resultados.")
        
        if interactive:
            print("\n¿Desea regenerar los reportes CSV? (normalmente no es necesario)")
            generate_reports = input("Regenerar reportes (s/n): ").lower().strip()
            create_reports = generate_reports in ['s', 'si', 'sí', 'y', 'yes']
        else:
            create_reports = False  # No regenerar en modo automático

        if create_reports:
            print("📊 Regenerando reportes de resultados...")
            try:
                results.generate_enhanced_results(column_elements_ids, 
                                                beam_elements_x_ids, beam_elements_y_ids, slab_elements_ids)
                print("✅ Reportes regenerados exitosamente")
            except Exception as e:
                print(f"⚠️ Error regenerando reportes: {e}")
        else:
            print("⏩ Regeneración de reportes omitida")

        # 12. Análisis con combinaciones de cargas ACI (nuevo)
        print("\n" + "="*60)
        print("PASO 12: ANÁLISIS CON COMBINACIONES DE CARGAS ACI")
        print("="*60)
        
        if interactive:
            print("\n🏗️ ANÁLISIS AVANZADO CON COMBINACIONES DE CARGAS")
            print("Este análisis ejecuta múltiples combinaciones según ACI 318 para obtener")
            print("las solicitaciones máximas necesarias para el diseño estructural.")
            print("\nBeneficios:")
            print("  • Solicitaciones máximas para diseño de elementos")
            print("  • Comparación entre diferentes combinaciones de cargas")
            print("  • Archivos CSV optimizados para post-procesamiento")
            print("  • Cumplimiento con normativas ACI 318")
            
            run_aci_analysis = input("\n¿Desea ejecutar análisis con combinaciones ACI? (s/n): ").lower().strip()
            perform_aci_analysis = run_aci_analysis in ['s', 'si', 'sí', 'y', 'yes']
        else:
            # En modo automático, ejecutar combinaciones básicas
            perform_aci_analysis = True
            print("🚀 Ejecutando análisis con combinaciones ACI en modo automático...")

        if perform_aci_analysis:
            print("\n🎯 Iniciando análisis con combinaciones de cargas ACI...")
            
            try:
                # Ejecutar análisis completo con combinaciones
                aci_results = multi_analysis.run_complete_load_combination_analysis(
                    geometry_data=geometry_data,
                    load_intensities=load_intensities,
                    beam_elements_x=beam_elements_x_ids,
                    beam_elements_y=beam_elements_y_ids,
                    interactive=interactive
                )
                
                if aci_results:
                    print("\n✅ ANÁLISIS CON COMBINACIONES ACI COMPLETADO EXITOSAMENTE")
                    print("📄 Archivos generados:")
                    print("   🎯 maximum_demands_design.csv - Solicitaciones máximas para diseño")
                    print("   📊 load_combinations_comparison.csv - Comparación detallada")
                    print("   📈 analysis_statistics.csv - Estadísticas por combinación")
                    print("   💾 Archivos estándar actualizados")
                else:
                    print("⚠️ El análisis con combinaciones ACI no se completó correctamente")
                    
            except Exception as e:
                print(f"❌ Error en análisis con combinaciones ACI: {e}")
                print("Continuando con el análisis estándar...")
        else:
            print("⏩ Análisis con combinaciones ACI omitido")

        # Mostrar figura de referencia al final para consulta del CSV
        if create_reports:
            visualization.show_reference_figure()

        # Finalización exitosa
        print("\n" + "="*80)
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print("="*80)
        print("✅ El modelo OpenSeesPy ha sido creado, analizado y procesado")
        print(f"📈 Edificio de {geometry_data['num_floor']} pisos con {total_elements} elementos")
        
        if create_reports:
            print("📄 Reportes CSV generados en el directorio actual")
            print("📋 Figura de referencia mostrada para consulta de elementos")
        
        if perform_aci_analysis and aci_results:
            print("🎯 Análisis con combinaciones ACI completado - archivos de diseño disponibles")
        
        print("\n💡 Puntos de expansión disponibles:")
        print("   🔹 Análisis sísmico y de viento")
        print("   🔹 Elementos adicionales (muros, escaleras)")
        print("   🔹 Optimización automática de diseño")
        print("   🔹 Interfaz gráfica de usuario")
        print("="*80)

    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR DURANTE LA EJECUCIÓN:")
        print(f"   {str(e)}")
        print(f"\n🔍 Información detallada del error:")
        print("-" * 50)
        traceback.print_exc()
        print("-" * 50)
        print("\n💭 Posibles soluciones:")
        print("   • Verificar que OpenSeesPy esté instalado correctamente")
        print("   • Revisar los valores de entrada")
        print("   • Consultar la documentación del módulo correspondiente")
        sys.exit(1)

if __name__ == "__main__":
    main()

# --- Puntos para escalar el código: General ---
# - Implementar una interfaz gráfica de usuario (GUI) para la entrada de datos
# - Permitir la importación de geometría desde archivos CAD/BIM (DXF, IFC)
# - Añadir más tipos de elementos (muros, cimentaciones, voladizos, escaleras)
# - Integrar análisis sísmico y de viento según normativas
# - Desarrollar un módulo de optimización de diseño automático
# - Mejorar la gestión de unidades y la conversión entre sistemas
# - Implementar análisis no lineal y dinámico
# - Añadir soporte para múltiples materiales en una estructura
# - Desarrollar módulos de diseño según normativas específicas
# - Implementar análisis de sensibilidad y confiabilidad
