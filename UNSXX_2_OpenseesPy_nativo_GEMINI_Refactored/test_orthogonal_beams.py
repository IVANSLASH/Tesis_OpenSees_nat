# test_orthogonal_beams.py
# ============================================
# Script de prueba para verificar que las vigas se generan
# correctamente de forma ortogonal sin elementos diagonales
# o inclinados.
# ============================================

import openseespy.opensees as ops
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import geometry
import enhanced_geometry
import input_data

def test_orthogonal_beams():
    """
    Prueba la generación de vigas ortogonales.
    """
    print("=" * 60)
    print("PRUEBA DE GENERACIÓN DE VIGAS ORTOGONALES")
    print("=" * 60)
    
    try:
        # Limpiar modelo
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)
        
        # Datos de prueba simples
        geometry_data = {
            "num_bay_x": 2,
            "num_bay_y": 2,
            "num_floor": 1,
            "bay_widths_x": [3.0, 3.0],
            "bay_widths_y": [3.0, 3.0],
            "story_heights": [3.0]
        }
        
        # Configuración de volados (sin volados para prueba simple)
        cantilever_config = {
            'front': None,
            'right': None,
            'left': None
        }
        
        # Propiedades de sección
        section_properties = {
            "E": 25000000.0,
            "A_viga": 0.15,
            "Iz_viga": 0.0028125,
            "Iy_viga": 0.0005,
            "J_viga": 0.0033125
        }
        
        print("1. Generando nodos...")
        total_nodes = geometry.create_nodes(geometry_data, 25000000.0, 0.49, 0, "-lMass")
        
        print("2. Generando columnas...")
        total_columns, column_elements_ids, next_ele_tag = geometry.create_columns(
            geometry_data, 25000000.0, 0, "-lMass",
            0.09, 0.000675, 0.000675, 0.00135
        )
        
        print("3. Generando vigas (deberían ser ortogonales)...")
        total_beams_x, beam_elements_x_ids, total_beams_y, beam_elements_y_ids, next_ele_tag = geometry.create_beams(
            geometry_data, 25000000.0, 0, "-lMass",
            0.15, 0.0028125, 0.0005, 0.0033125,
            next_ele_tag, total_nodes
        )
        
        print(f"\n✅ RESULTADOS DE LA PRUEBA:")
        print(f"   Nodos generados: {total_nodes}")
        print(f"   Columnas generadas: {total_columns}")
        print(f"   Vigas en X generadas: {total_beams_x}")
        print(f"   Vigas en Y generadas: {total_beams_y}")
        
        # Verificar que las vigas son ortogonales
        print(f"\n🔍 VERIFICANDO ORTOGONALIDAD DE VIGAS:")
        
        all_beams = beam_elements_x_ids + beam_elements_y_ids
        diagonal_beams = 0
        inclined_beams = 0
        orthogonal_beams = 0
        
        for beam_id in all_beams:
            try:
                nodes = ops.eleNodes(beam_id)
                if len(nodes) >= 2:
                    coord1 = ops.nodeCoord(nodes[0])
                    coord2 = ops.nodeCoord(nodes[1])
                    
                    # Calcular diferencias
                    dx = abs(coord1[0] - coord2[0])
                    dy = abs(coord1[1] - coord2[1])
                    dz = abs(coord1[2] - coord2[2])
                    
                    # Clasificar la viga
                    if dx > 0.001 and dy > 0.001:
                        diagonal_beams += 1
                        print(f"   ❌ Viga diagonal detectada: {beam_id} (nodos {nodes[0]}-{nodes[1]})")
                    elif dz > 0.001:
                        inclined_beams += 1
                        print(f"   ❌ Viga inclinada detectada: {beam_id} (nodos {nodes[0]}-{nodes[1]})")
                    else:
                        orthogonal_beams += 1
                        print(f"   ✅ Viga ortogonal confirmada: {beam_id} (nodos {nodes[0]}-{nodes[1]})")
                        
            except Exception as e:
                print(f"   ⚠️ Error verificando viga {beam_id}: {e}")
        
        print(f"\n📊 RESUMEN DE VERIFICACIÓN:")
        print(f"   Vigas ortogonales: {orthogonal_beams}")
        print(f"   Vigas diagonales: {diagonal_beams}")
        print(f"   Vigas inclinadas: {inclined_beams}")
        
        if diagonal_beams == 0 and inclined_beams == 0:
            print(f"\n🎉 ¡PRUEBA EXITOSA! Todas las vigas son ortogonales.")
            return True
        else:
            print(f"\n❌ PRUEBA FALLIDA: Se detectaron vigas no ortogonales.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        return False

def test_enhanced_orthogonal_beams():
    """
    Prueba la generación de vigas ortogonales con geometría mejorada.
    """
    print("\n" + "=" * 60)
    print("PRUEBA DE GENERACIÓN DE VIGAS ORTOGONALES MEJORADAS")
    print("=" * 60)
    
    try:
        # Limpiar modelo
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)
        
        # Datos de prueba con volados
        geometry_data = {
            "num_bay_x": 2,
            "num_bay_y": 2,
            "num_floor": 1,
            "bay_widths_x": [3.0, 3.0],
            "bay_widths_y": [3.0, 3.0],
            "story_heights": [3.0],
            "section_properties": {
                "E": 25000000.0,
                "A_viga": 0.15,
                "Iz_viga": 0.0028125,
                "Iy_viga": 0.0005,
                "J_viga": 0.0033125
            }
        }
        
        # Configuración de volados
        cantilever_config = {
            'front': {
                'length': 1.5,
                'edge_beam': {
                    'A': 0.12,
                    'Iz': 0.002,
                    'Iy': 0.0004
                }
            },
            'right': None,
            'left': None
        }
        
        # Configuración de columnas
        column_config = {
            'type': 'uniform',
            'lx_col': 0.30,
            'ly_col': 0.30,
            'A_col': 0.09,
            'Iz_col': 0.000675,
            'Iy_col': 0.000675
        }
        
        print("1. Generando nodos mejorados...")
        total_nodes, node_mapping, extended_x_coords, extended_y_coords, z_coords = enhanced_geometry.generate_enhanced_nodes(
            geometry_data, cantilever_config
        )
        
        print("2. Generando columnas mejoradas...")
        column_elements_ids, next_ele_tag = enhanced_geometry.generate_enhanced_column_elements(
            node_mapping, geometry_data, column_config, extended_x_coords, extended_y_coords, z_coords
        )
        
        print("3. Generando vigas mejoradas (deberían ser ortogonales)...")
        beam_elements_x_ids, beam_elements_y_ids, cantilever_beam_ids, next_ele_tag = enhanced_geometry.generate_enhanced_beam_elements(
            node_mapping, geometry_data, cantilever_config, extended_x_coords, extended_y_coords, z_coords, next_ele_tag
        )
        
        print(f"\n✅ RESULTADOS DE LA PRUEBA MEJORADA:")
        print(f"   Nodos generados: {total_nodes}")
        print(f"   Columnas generadas: {len(column_elements_ids)}")
        print(f"   Vigas en X generadas: {len(beam_elements_x_ids)}")
        print(f"   Vigas en Y generadas: {len(beam_elements_y_ids)}")
        print(f"   Vigas de volado generadas: {len(cantilever_beam_ids)}")
        
        # Verificar que todas las vigas son ortogonales
        print(f"\n🔍 VERIFICANDO ORTOGONALIDAD DE VIGAS MEJORADAS:")
        
        all_beams = beam_elements_x_ids + beam_elements_y_ids + cantilever_beam_ids
        diagonal_beams = 0
        inclined_beams = 0
        orthogonal_beams = 0
        
        for beam_id in all_beams:
            try:
                nodes = ops.eleNodes(beam_id)
                if len(nodes) >= 2:
                    coord1 = ops.nodeCoord(nodes[0])
                    coord2 = ops.nodeCoord(nodes[1])
                    
                    # Calcular diferencias
                    dx = abs(coord1[0] - coord2[0])
                    dy = abs(coord1[1] - coord2[1])
                    dz = abs(coord1[2] - coord2[2])
                    
                    # Clasificar la viga
                    if dx > 0.001 and dy > 0.001:
                        diagonal_beams += 1
                        print(f"   ❌ Viga diagonal detectada: {beam_id} (nodos {nodes[0]}-{nodes[1]})")
                    elif dz > 0.001:
                        inclined_beams += 1
                        print(f"   ❌ Viga inclinada detectada: {beam_id} (nodos {nodes[0]}-{nodes[1]})")
                    else:
                        orthogonal_beams += 1
                        print(f"   ✅ Viga ortogonal confirmada: {beam_id} (nodos {nodes[0]}-{nodes[1]})")
                        
            except Exception as e:
                print(f"   ⚠️ Error verificando viga {beam_id}: {e}")
        
        print(f"\n📊 RESUMEN DE VERIFICACIÓN MEJORADA:")
        print(f"   Vigas ortogonales: {orthogonal_beams}")
        print(f"   Vigas diagonales: {diagonal_beams}")
        print(f"   Vigas inclinadas: {inclined_beams}")
        
        if diagonal_beams == 0 and inclined_beams == 0:
            print(f"\n🎉 ¡PRUEBA MEJORADA EXITOSA! Todas las vigas son ortogonales.")
            return True
        else:
            print(f"\n❌ PRUEBA MEJORADA FALLIDA: Se detectaron vigas no ortogonales.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error en la prueba mejorada: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de vigas ortogonales...")
    
    # Prueba básica
    test1_success = test_orthogonal_beams()
    
    # Prueba mejorada
    test2_success = test_enhanced_orthogonal_beams()
    
    print("\n" + "=" * 60)
    print("RESUMEN FINAL DE PRUEBAS")
    print("=" * 60)
    print(f"Prueba básica: {'✅ EXITOSA' if test1_success else '❌ FALLIDA'}")
    print(f"Prueba mejorada: {'✅ EXITOSA' if test2_success else '❌ FALLIDA'}")
    
    if test1_success and test2_success:
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("Las correcciones han eliminado las vigas diagonales e inclinadas.")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar el código.") 