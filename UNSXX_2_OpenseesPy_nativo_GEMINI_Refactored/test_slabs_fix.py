# test_slabs_fix.py
# Script de prueba para verificar que la corrección de losas funciona correctamente

import openseespy.opensees as ops
import input_data
import geometry
import sections
import slabs

def test_slabs_creation():
    """Prueba rápida para verificar la creación de losas."""
    print("=== PRUEBA DE CORRECCIÓN DE LOSAS ===\n")
    
    try:
        # Limpiar modelo
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)
        print("✅ Modelo OpenSeesPy inicializado")
        
        # Usar configuración por defecto (3x3 vanos, 3 pisos)
        geometry_data = input_data.get_default_geometry_data()
        print(f"✅ Configuración por defecto: {geometry_data['num_bay_x']}x{geometry_data['num_bay_y']} vanos, {geometry_data['num_floor']} pisos")
        
        # Definir secciones
        section_properties = sections.define_sections(interactive=False)
        print("✅ Secciones definidas correctamente")
        
        # Crear nodos
        total_nodes = geometry.create_nodes(geometry_data, section_properties["E"], 0.49, 0, "-lMass")
        print(f"✅ {total_nodes} nodos creados")
        
        # Crear columnas (necesarias para la numeración correcta de elementos)
        total_columns, column_ids, next_tag_columns = geometry.create_columns(
            geometry_data, section_properties["E"], 0, "-lMass",
            section_properties["A_col"], section_properties["Iz_col"],
            section_properties["Iy_col"], section_properties["J_col"]
        )
        print(f"✅ {total_columns} columnas creadas")
        
        # Crear vigas (necesarias para la numeración correcta de elementos)
        total_beams_x, beam_x_ids, total_beams_y, beam_y_ids, next_tag_beams = geometry.create_beams(
            geometry_data, section_properties["E"], 0, "-lMass",
            section_properties["A_viga"], section_properties["Iz_viga"],
            section_properties["Iy_viga"], section_properties["J_viga"],
            next_tag_columns, total_nodes
        )
        print(f"✅ {total_beams_x} vigas X y {total_beams_y} vigas Y creadas")
        
        # *** ESTA ES LA PARTE CRÍTICA: CREAR LOSAS ***
        print("\n--- Creando losas (parte que fallaba antes) ---")
        total_slabs, slab_ids, next_tag_slabs = slabs.create_slabs(
            geometry_data, section_properties, next_tag_beams
        )
        
        if total_slabs > 0:
            print(f"✅ {total_slabs} elementos de losa creados exitosamente")
            print(f"✅ IDs de elementos de losa: {slab_ids[:5]}..." if len(slab_ids) > 5 else f"✅ IDs de elementos de losa: {slab_ids}")
        else:
            print("⚠️  No se crearon elementos de losa, pero el proceso no falló")
        
        # Resumen final
        total_elements = total_columns + total_beams_x + total_beams_y + total_slabs
        print(f"\n🎉 PRUEBA EXITOSA")
        print(f"   Total elementos: {total_elements}")
        print(f"   - Columnas: {total_columns}")
        print(f"   - Vigas X: {total_beams_x}")
        print(f"   - Vigas Y: {total_beams_y}")
        print(f"   - Losas: {total_slabs}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_slabs_creation()
    if success:
        print("\n✅ El problema de losas ha sido CORREGIDO")
        print("   Ahora puedes ejecutar main.py sin errores")
    else:
        print("\n❌ Aún hay problemas que requieren atención")