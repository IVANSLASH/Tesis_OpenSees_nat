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
import visualization
import results

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
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)
        print("✓ Modelo 3D creado (6 DOF por nodo)")

        # 1. Entrada de datos geométricos
        print("\n" + "="*60)
        print("PASO 1: CONFIGURACIÓN GEOMÉTRICA")
        print("="*60)
        
        geometry_data = input_data.get_building_geometry_data(
            interactive=interactive, 
            config_file=config_file
        )

        # 2. Definición de secciones y materiales
        print("\n" + "="*60)
        print("PASO 2: DEFINICIÓN DE MATERIALES Y SECCIONES")
        print("="*60)
        
        section_properties = sections.define_sections(
            interactive=interactive,
            material_choice="concreto_f21" if not interactive else None
        )

        # 3. Configuración de intensidades de carga
        print("\n" + "="*60)
        print("PASO 3: CONFIGURACIÓN DE CARGAS")
        print("="*60)
        
        load_intensities = loads.get_load_intensities(interactive=interactive)

        # Propiedades de material y masa para nodos y elementos
        E_material = section_properties["E"]
        massX = 0.49  # Masa en dirección X (ton)
        M = 0         # Masa adicional para elementos (ton)
        massType = "-lMass"  # Tipo de masa (masa distribuida)

        # 4. Creación de nodos
        print("\n" + "="*60)
        print("PASO 4: GENERACIÓN DE NODOS")
        print("="*60)
        
        total_nodes = geometry.create_nodes(geometry_data, E_material, massX, M, massType)

        # 5. Creación de columnas
        print("\n" + "="*60)
        print("PASO 5: GENERACIÓN DE COLUMNAS")
        print("="*60)
        
        total_columns, column_elements_ids, next_ele_tag_after_columns = geometry.create_columns(
            geometry_data, E_material, M, massType,
            section_properties["A_col"], section_properties["Iz_col"],
            section_properties["Iy_col"], section_properties["J_col"]
        )

        # 6. Creación de vigas
        print("\n" + "="*60)
        print("PASO 6: GENERACIÓN DE VIGAS")
        print("="*60)
        
        total_beams_x, beam_elements_x_ids, total_beams_y, beam_elements_y_ids, next_ele_tag_after_beams = geometry.create_beams(
            geometry_data, E_material, M, massType,
            section_properties["A_viga"], section_properties["Iz_viga"],
            section_properties["Iy_viga"], section_properties["J_viga"],
            next_ele_tag_after_columns, total_nodes
        )

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
        
        analysis.run_analysis()

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
            print("🎨 Generando visualizaciones...")
            
            # Modelo y deformada
            visualization.plot_model_and_defo(geometry_data["num_floor"], total_nodes, total_elements)
            
            # Secciones extruidas
            visualization.plot_extruded_sections(geometry_data, section_properties, 
                                               column_elements_ids, beam_elements_x_ids, beam_elements_y_ids)
            
            # Detalles de secciones
            visualization.plot_section_details(section_properties)
            
            # Comparación de secciones
            visualization.plot_section_comparison(section_properties)
            
            # Diagramas de fuerzas internas
            visualization.plot_section_force_diagrams()
        else:
            print("⏩ Visualización omitida")

        # 11. Generación de resultados
        print("\n" + "="*60)
        print("PASO 11: GENERACIÓN DE REPORTES")
        print("="*60)
        
        if interactive:
            generate_reports = input("\n¿Desea generar reportes CSV de resultados? (s/n): ").lower().strip()
            create_reports = generate_reports in ['s', 'si', 'sí', 'y', 'yes']
        else:
            create_reports = True

        if create_reports:
            print("📊 Generando reportes de resultados...")
            results.generate_results(total_nodes, column_elements_ids, 
                                    beam_elements_x_ids, beam_elements_y_ids, slab_elements_ids)
        else:
            print("⏩ Generación de reportes omitida")

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
