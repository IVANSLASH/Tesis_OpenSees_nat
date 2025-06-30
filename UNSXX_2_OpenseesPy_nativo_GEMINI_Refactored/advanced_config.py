# advanced_config.py
# ============================================
# Módulo para configuraciones avanzadas del modelo estructural:
# - Secciones de columnas personalizadas (uniformes, exterior/interior, por grupos)
# - Volados frontales con vigas de borde planas
# - Volados laterales en dirección Y
# - Menús interactivos para configuración
# ============================================

import numpy as np

def column_configuration_menu():
    """
    Menú interactivo para configurar las secciones de columnas.
    """
    print("\n" + "="*60)
    print("🏗️  CONFIGURACIÓN DE SECCIONES DE COLUMNAS")
    print("="*60)
    print("Seleccione el tipo de configuración para las columnas:")
    print()
    print("1️⃣  Todas las columnas con la misma sección (uniforme)")
    print("2️⃣  Columnas exteriores e interiores con secciones diferentes")
    print("3️⃣  Secciones personalizadas por grupo de columnas")
    print("0️⃣  Usar configuración por defecto")
    print()
    
    while True:
        try:
            choice = input("Ingrese su opción (0-3): ").strip()
            if choice in ['0', '1', '2', '3']:
                return choice
            else:
                print("❌ Opción inválida. Por favor ingrese un número del 0 al 3.")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada por el usuario")
            return '0'

def get_uniform_column_section():
    """
    Obtiene las dimensiones para columnas uniformes.
    """
    print("\n📐 CONFIGURACIÓN DE COLUMNAS UNIFORMES")
    print("-" * 40)
    print("Todas las columnas tendrán las mismas dimensiones.")
    print()
    
    while True:
        try:
            lx = float(input("Ingrese dimensión LX de columna (m) [0.25-0.80]: ").strip())
            if 0.25 <= lx <= 0.80:
                break
            else:
                print("❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return None
    
    while True:
        try:
            ly = float(input("Ingrese dimensión LY de columna (m) [0.25-0.80]: ").strip())
            if 0.25 <= ly <= 0.80:
                break
            else:
                print("❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return None
    
    return {
        'type': 'uniform',
        'lx_col': lx,
        'ly_col': ly,
        'A_col': lx * ly,
        'Iz_col': (lx * ly**3) / 12,
        'Iy_col': (ly * lx**3) / 12
    }

def get_exterior_interior_column_sections():
    """
    Obtiene las dimensiones para columnas exteriores e interiores.
    """
    print("\n🏢 CONFIGURACIÓN DE COLUMNAS EXTERIORES E INTERIORES")
    print("-" * 55)
    print("Las columnas exteriores y interiores tendrán dimensiones diferentes.")
    print()
    
    # Columnas exteriores
    print("🔸 COLUMNAS EXTERIORES (perimetrales):")
    while True:
        try:
            lx_ext = float(input("  LX exterior (m) [0.25-0.80]: ").strip())
            if 0.25 <= lx_ext <= 0.80:
                break
            else:
                print("  ❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
        except ValueError:
            print("  ❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return None
    
    while True:
        try:
            ly_ext = float(input("  LY exterior (m) [0.25-0.80]: ").strip())
            if 0.25 <= ly_ext <= 0.80:
                break
            else:
                print("  ❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
        except ValueError:
            print("  ❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return None
    
    print()
    # Columnas interiores
    print("🔹 COLUMNAS INTERIORES (centrales):")
    while True:
        try:
            lx_int = float(input("  LX interior (m) [0.25-0.80]: ").strip())
            if 0.25 <= lx_int <= 0.80:
                break
            else:
                print("  ❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
        except ValueError:
            print("  ❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return None
    
    while True:
        try:
            ly_int = float(input("  LY interior (m) [0.25-0.80]: ").strip())
            if 0.25 <= ly_int <= 0.80:
                break
            else:
                print("  ❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
        except ValueError:
            print("  ❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return None
    
    return {
        'type': 'exterior_interior',
        'exterior': {
            'lx_col': lx_ext,
            'ly_col': ly_ext,
            'A_col': lx_ext * ly_ext,
            'Iz_col': (lx_ext * ly_ext**3) / 12,
            'Iy_col': (ly_ext * lx_ext**3) / 12
        },
        'interior': {
            'lx_col': lx_int,
            'ly_col': ly_int,
            'A_col': lx_int * ly_int,
            'Iz_col': (lx_int * ly_int**3) / 12,
            'Iy_col': (ly_int * lx_int**3) / 12
        }
    }

def get_custom_column_groups(geometry_data):
    """
    Obtiene las dimensiones personalizadas por grupo de columnas.
    """
    print("\n🎯 CONFIGURACIÓN PERSONALIZADA POR GRUPOS DE COLUMNAS")
    print("-" * 60)
    
    # Calcular número de grupos de columnas
    bay_widths_x = geometry_data["bay_widths_x"]
    bay_widths_y = geometry_data["bay_widths_y"]
    
    num_columns_x = len(bay_widths_x) + 1
    num_columns_y = len(bay_widths_y) + 1
    total_column_groups = num_columns_x * num_columns_y
    
    print(f"Su estructura tiene {num_columns_x} x {num_columns_y} = {total_column_groups} grupos de columnas")
    print("Cada grupo representa columnas en la misma posición (X,Y) desde nivel 0 hasta el último nivel.")
    print()
    
    # Mostrar disposición de grupos
    print("📍 DISPOSICIÓN DE GRUPOS DE COLUMNAS:")
    print("   ", end="")
    for j in range(num_columns_y):
        print(f"   Y{j+1:2d}", end="")
    print()
    
    for i in range(num_columns_x):
        print(f"X{i+1:2d}", end="")
        for j in range(num_columns_y):
            group_id = i * num_columns_y + j + 1
            print(f"  G{group_id:3d}", end="")
        print()
    
    print()
    print("¿Desea configurar cada grupo individualmente?")
    print("1️⃣  Sí, configurar cada grupo")
    print("2️⃣  No, usar dimensiones por defecto con variación automática")
    
    while True:
        try:
            choice = input("Seleccione opción (1-2): ").strip()
            if choice == '1':
                return get_individual_group_config(num_columns_x, num_columns_y)
            elif choice == '2':
                return get_automatic_group_variation(num_columns_x, num_columns_y)
            else:
                print("❌ Opción inválida. Ingrese 1 o 2.")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return None

def get_individual_group_config(num_columns_x, num_columns_y):
    """
    Configuración individual de cada grupo de columnas.
    """
    print("\n🔧 CONFIGURACIÓN INDIVIDUAL DE GRUPOS")
    print("-" * 45)
    
    groups = {}
    total_groups = num_columns_x * num_columns_y
    
    for i in range(num_columns_x):
        for j in range(num_columns_y):
            group_id = i * num_columns_y + j + 1
            
            # Determinar tipo de columna
            is_corner = (i == 0 or i == num_columns_x-1) and (j == 0 or j == num_columns_y-1)
            is_edge = (i == 0 or i == num_columns_x-1 or j == 0 or j == num_columns_y-1) and not is_corner
            is_interior = not is_corner and not is_edge
            
            position_type = "esquina" if is_corner else ("borde" if is_edge else "interior")
            
            print(f"\n📍 Grupo G{group_id} (X{i+1}, Y{j+1}) - Columna de {position_type}:")
            
            while True:
                try:
                    lx = float(input(f"    LX (m) [0.25-0.80]: ").strip())
                    if 0.25 <= lx <= 0.80:
                        break
                    else:
                        print("    ❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
                except ValueError:
                    print("    ❌ Ingrese un valor numérico válido")
                except KeyboardInterrupt:
                    print("\n⚠️ Configuración cancelada")
                    return None
            
            while True:
                try:
                    ly = float(input(f"    LY (m) [0.25-0.80]: ").strip())
                    if 0.25 <= ly <= 0.80:
                        break
                    else:
                        print("    ❌ Dimensión fuera de rango. Use valores entre 0.25 y 0.80 m")
                except ValueError:
                    print("    ❌ Ingrese un valor numérico válido")
                except KeyboardInterrupt:
                    print("\n⚠️ Configuración cancelada")
                    return None
            
            groups[group_id] = {
                'lx_col': lx,
                'ly_col': ly,
                'A_col': lx * ly,
                'Iz_col': (lx * ly**3) / 12,
                'Iy_col': (ly * lx**3) / 12,
                'position_x': i,
                'position_y': j,
                'type': position_type
            }
            
            print(f"    ✅ Grupo G{group_id}: {lx:.2f}x{ly:.2f}m configurado")
    
    return {
        'type': 'custom_groups',
        'groups': groups,
        'num_columns_x': num_columns_x,
        'num_columns_y': num_columns_y
    }

def get_automatic_group_variation(num_columns_x, num_columns_y):
    """
    Genera variación automática de dimensiones por tipo de columna.
    """
    print("\n🤖 CONFIGURACIÓN AUTOMÁTICA CON VARIACIÓN")
    print("-" * 45)
    print("Las dimensiones se asignarán automáticamente según la posición:")
    print("  - Columnas de esquina: Más robustas")
    print("  - Columnas de borde: Dimensiones intermedias")
    print("  - Columnas interiores: Según cargas")
    print()
    
    # Dimensiones base
    base_lx = 0.30  # Dimensión base
    base_ly = 0.30
    
    groups = {}
    
    for i in range(num_columns_x):
        for j in range(num_columns_y):
            group_id = i * num_columns_y + j + 1
            
            # Determinar tipo y factor de escala
            is_corner = (i == 0 or i == num_columns_x-1) and (j == 0 or j == num_columns_y-1)
            is_edge = (i == 0 or i == num_columns_x-1 or j == 0 or j == num_columns_y-1) and not is_corner
            is_interior = not is_corner and not is_edge
            
            if is_corner:
                factor = 1.2  # 20% más robustas
                position_type = "esquina"
            elif is_edge:
                factor = 1.1  # 10% más robustas
                position_type = "borde"
            else:
                factor = 1.0  # Dimensiones base
                position_type = "interior"
            
            lx = min(base_lx * factor, 0.80)  # Límite máximo
            ly = min(base_ly * factor, 0.80)
            
            groups[group_id] = {
                'lx_col': lx,
                'ly_col': ly,
                'A_col': lx * ly,
                'Iz_col': (lx * ly**3) / 12,
                'Iy_col': (ly * lx**3) / 12,
                'position_x': i,
                'position_y': j,
                'type': position_type
            }
            
            print(f"  G{group_id} (X{i+1},Y{j+1}) - {position_type}: {lx:.2f}x{ly:.2f}m")
    
    return {
        'type': 'custom_groups',
        'groups': groups,
        'num_columns_x': num_columns_x,
        'num_columns_y': num_columns_y
    }

def cantilever_configuration_menu():
    """
    Menú para configurar volados (cantilevers).
    """
    print("\n" + "="*60)
    print("🏗️  CONFIGURACIÓN DE VOLADOS")
    print("="*60)
    print("Los volados permiten ganar área útil a partir del segundo nivel.")
    print("Típicos en edificaciones de Bolivia y similares.")
    print()
    print("Opciones disponibles:")
    print("1️⃣  Volado frontal (dirección X)")
    print("2️⃣  Volado lateral derecho (dirección Y+)")
    print("3️⃣  Volado lateral izquierdo (dirección Y-)")
    print("4️⃣  Combinación de volados")
    print("0️⃣  Sin volados")
    print()
    
    while True:
        try:
            choice = input("Ingrese su opción (0-4): ").strip()
            if choice in ['0', '1', '2', '3', '4']:
                return choice
            else:
                print("❌ Opción inválida. Por favor ingrese un número del 0 al 4.")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada por el usuario")
            return '0'

def get_cantilever_config(choice, geometry_data):
    """
    Obtiene la configuración específica de volados según la elección.
    """
    config = {
        'front': None,
        'right': None,
        'left': None
    }
    
    if choice == '0':
        return config
    elif choice == '1':
        config['front'] = get_front_cantilever_config()
    elif choice == '2':
        config['right'] = get_side_cantilever_config('derecho')
    elif choice == '3':
        config['left'] = get_side_cantilever_config('izquierdo')
    elif choice == '4':
        config = get_combined_cantilever_config()
    
    return config

def get_front_cantilever_config():
    """
    Configuración del volado frontal.
    """
    print("\n🏢 CONFIGURACIÓN DE VOLADO FRONTAL")
    print("-" * 40)
    print("El volado frontal se extiende en la dirección X positiva.")
    print("Se aplicará desde el segundo nivel hacia arriba.")
    print()
    
    while True:
        try:
            length = float(input("Longitud del volado frontal (m) [0.3-1.0]: ").strip())
            if 0.3 <= length <= 1.0:
                break
            else:
                print("❌ Longitud fuera de rango. Use valores entre 0.3 y 1.0 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    print("\n🔧 CONFIGURACIÓN DE VIGA DE BORDE PLANA:")
    print("Esta viga soportará el borde del volado.")
    
    while True:
        try:
            width = float(input("Ancho de viga de borde (m) [0.20-0.40]: ").strip())
            if 0.20 <= width <= 0.40:
                break
            else:
                print("❌ Ancho fuera de rango. Use valores entre 0.20 y 0.40 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    while True:
        try:
            height = float(input("Altura de viga de borde (m) [0.15-0.30]: ").strip())
            if 0.15 <= height <= 0.30:
                break
            else:
                print("❌ Altura fuera de rango. Use valores entre 0.15 y 0.30 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    return {
        'length': length,
        'edge_beam': {
            'width': width,
            'height': height,
            'A': width * height,
            'Iz': (width * height**3) / 12,
            'Iy': (height * width**3) / 12
        },
        'start_level': 2  # Desde el segundo nivel
    }

def get_side_cantilever_config(side):
    """
    Configuración de volado lateral.
    """
    print(f"\n🏢 CONFIGURACIÓN DE VOLADO LATERAL {side.upper()}")
    print("-" * 50)
    print(f"El volado lateral {side} se extiende en la dirección Y.")
    print("Limitado a máximo 1.0 m, idealmente 0.6 m.")
    print()
    
    while True:
        try:
            length = float(input(f"Longitud del volado {side} (m) [0.3-1.0]: ").strip())
            if 0.3 <= length <= 1.0:
                if length > 0.6:
                    confirm = input(f"⚠️  Longitud {length}m es mayor a la ideal (0.6m). ¿Continuar? (s/n): ").strip().lower()
                    if confirm in ['s', 'si', 'y', 'yes']:
                        break
                    else:
                        continue
                else:
                    break
            else:
                print("❌ Longitud fuera de rango. Use valores entre 0.3 y 1.0 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    print("\n🔧 CONFIGURACIÓN DE VIGA DE BORDE LATERAL:")
    
    while True:
        try:
            width = float(input("Ancho de viga de borde (m) [0.20-0.35]: ").strip())
            if 0.20 <= width <= 0.35:
                break
            else:
                print("❌ Ancho fuera de rango. Use valores entre 0.20 y 0.35 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    while True:
        try:
            height = float(input("Altura de viga de borde (m) [0.15-0.25]: ").strip())
            if 0.15 <= height <= 0.25:
                break
            else:
                print("❌ Altura fuera de rango. Use valores entre 0.15 y 0.25 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    return {
        'length': length,
        'edge_beam': {
            'width': width,
            'height': height,
            'A': width * height,
            'Iz': (width * height**3) / 12,
            'Iy': (height * width**3) / 12
        },
        'start_level': 2  # Desde el segundo nivel
    }

def get_combined_cantilever_config():
    """
    Configuración combinada de múltiples volados.
    """
    print("\n🏗️  CONFIGURACIÓN COMBINADA DE VOLADOS")
    print("-" * 45)
    print("Puede combinar volado frontal con volados laterales.")
    print()
    
    config = {
        'front': None,
        'right': None,
        'left': None
    }
    
    # Volado frontal
    add_front = input("¿Agregar volado frontal? (s/n): ").strip().lower()
    if add_front in ['s', 'si', 'y', 'yes']:
        config['front'] = get_front_cantilever_config()
        if config['front'] is None:
            return None
    
    # Volado lateral derecho
    add_right = input("¿Agregar volado lateral derecho? (s/n): ").strip().lower()
    if add_right in ['s', 'si', 'y', 'yes']:
        config['right'] = get_side_cantilever_config('derecho')
        if config['right'] is None:
            return None
    
    # Volado lateral izquierdo
    add_left = input("¿Agregar volado lateral izquierdo? (s/n): ").strip().lower()
    if add_left in ['s', 'si', 'y', 'yes']:
        config['left'] = get_side_cantilever_config('izquierdo')
        if config['left'] is None:
            return None
    
    return config

def slab_type_configuration_menu():
    """
    Menú para configurar el tipo de losa.
    """
    print("\n" + "="*60)
    print("🏢 CONFIGURACIÓN DE TIPO DE LOSA")
    print("="*60)
    print("Seleccione el tipo de losa para su estructura:")
    print()
    print("1️⃣  Losa maciza (sólida)")
    print("    • Espesor uniforme en toda la superficie")
    print("    • Mayor resistencia y rigidez")
    print("    • Ideal para luces cortas y medianas")
    print()
    print("2️⃣  Losa nervada (aligerada)")
    print("    • Con nervios en una dirección")
    print("    • Menor peso propio")
    print("    • Ideal para luces grandes")
    print()
    
    while True:
        try:
            choice = input("Ingrese su opción (1-2): ").strip()
            if choice in ['1', '2']:
                return choice
            else:
                print("❌ Opción inválida. Por favor ingrese 1 o 2.")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada por el usuario")
            return '1'  # Por defecto losa maciza

def get_slab_configuration(choice):
    """
    Obtiene la configuración específica del tipo de losa.
    """
    if choice == '1':
        return get_solid_slab_config()
    elif choice == '2':
        return get_ribbed_slab_config()

def get_solid_slab_config():
    """
    Configuración para losa maciza.
    """
    print("\n🏗️ CONFIGURACIÓN DE LOSA MACIZA")
    print("-" * 40)
    print("Las losas macizas son elementos bidimensionales uniformes.")
    print("Se modelan como elementos shell o mediante discretización.")
    print()
    
    while True:
        try:
            thickness = float(input("Espesor de losa maciza (m) [0.10-0.30]: ").strip())
            if 0.10 <= thickness <= 0.30:
                break
            else:
                print("❌ Espesor fuera de rango. Use valores entre 0.10 y 0.30 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    return {
        'type': 'solid',
        'thickness': thickness,
        'description': f'Losa maciza de {thickness:.2f}m de espesor',
        'load_factor': 1.0,  # Factor para cálculo de cargas
        'self_weight': thickness * 25.0  # kN/m³ * espesor = kN/m²
    }

def get_ribbed_slab_config():
    """
    Configuración para losa nervada.
    """
    print("\n🏗️ CONFIGURACIÓN DE LOSA NERVADA")
    print("-" * 40)
    print("Las losas nervadas tienen nervios en una dirección principal.")
    print("Son más eficientes para luces grandes y reducen el peso propio.")
    print()
    
    # Selección de dirección
    print("📐 DIRECCIÓN DE LOS NERVIOS:")
    print("1️⃣  Nervios en dirección X (paralelos al eje X)")
    print("2️⃣  Nervios en dirección Y (paralelos al eje Y)")
    print()
    
    while True:
        try:
            direction_choice = input("Seleccione la dirección de los nervios (1-2): ").strip()
            if direction_choice in ['1', '2']:
                break
            else:
                print("❌ Opción inválida. Ingrese 1 o 2.")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    direction = 'X' if direction_choice == '1' else 'Y'
    direction_desc = 'dirección X' if direction == 'X' else 'dirección Y'
    
    print(f"\n🔧 DIMENSIONES DE LOSA NERVADA (nervios en {direction_desc}):")
    
    # Espesor de losa superior
    while True:
        try:
            top_slab = float(input("Espesor de losa superior (m) [0.05-0.15]: ").strip())
            if 0.05 <= top_slab <= 0.15:
                break
            else:
                print("❌ Espesor fuera de rango. Use valores entre 0.05 y 0.15 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    # Altura total de la losa
    while True:
        try:
            total_height = float(input("Altura total de la losa (m) [0.20-0.50]: ").strip())
            if 0.20 <= total_height <= 0.50:
                if total_height <= top_slab:
                    print("❌ La altura total debe ser mayor al espesor de la losa superior")
                    continue
                break
            else:
                print("❌ Altura fuera de rango. Use valores entre 0.20 y 0.50 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    # Ancho de nervios
    while True:
        try:
            rib_width = float(input("Ancho de nervios (m) [0.10-0.25]: ").strip())
            if 0.10 <= rib_width <= 0.25:
                break
            else:
                print("❌ Ancho fuera de rango. Use valores entre 0.10 y 0.25 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    # Separación entre nervios
    while True:
        try:
            rib_spacing = float(input("Separación entre nervios (m) [0.60-1.00]: ").strip())
            if 0.60 <= rib_spacing <= 1.00:
                break
            else:
                print("❌ Separación fuera de rango. Use valores entre 0.60 y 1.00 m")
        except ValueError:
            print("❌ Ingrese un valor numérico válido")
        except KeyboardInterrupt:
            print("\n⚠️ Configuración cancelada")
            return None
    
    # Calcular peso propio equivalente
    rib_height = total_height - top_slab
    concrete_volume_ratio = (top_slab + (rib_width * rib_height) / rib_spacing) / total_height
    equivalent_thickness = total_height * concrete_volume_ratio
    self_weight = equivalent_thickness * 25.0  # kN/m³ * espesor = kN/m²
    
    return {
        'type': 'ribbed',
        'direction': direction,
        'direction_description': direction_desc,
        'top_slab_thickness': top_slab,
        'total_height': total_height,
        'rib_width': rib_width,
        'rib_spacing': rib_spacing,
        'rib_height': rib_height,
        'equivalent_thickness': equivalent_thickness,
        'description': f'Losa nervada H={total_height:.2f}m, nervios en {direction_desc}',
        'load_factor': 0.8,  # Factor de reducción por aligeramiento
        'self_weight': self_weight
    }

def display_configuration_summary(column_config, cantilever_config, slab_config=None):
    """
    Muestra un resumen de la configuración seleccionada.
    """
    print("\n" + "="*60)
    print("📋 RESUMEN DE CONFIGURACIÓN AVANZADA")
    print("="*60)
    
    # Resumen de columnas
    print("\n🏗️  CONFIGURACIÓN DE COLUMNAS:")
    if column_config['type'] == 'uniform':
        print(f"  ✅ Columnas uniformes: {column_config['lx_col']:.2f} x {column_config['ly_col']:.2f} m")
    elif column_config['type'] == 'exterior_interior':
        ext = column_config['exterior']
        int_col = column_config['interior']
        print(f"  ✅ Columnas exteriores: {ext['lx_col']:.2f} x {ext['ly_col']:.2f} m")
        print(f"  ✅ Columnas interiores: {int_col['lx_col']:.2f} x {int_col['ly_col']:.2f} m")
    elif column_config['type'] == 'custom_groups':
        groups = column_config['groups']
        print(f"  ✅ Configuración personalizada: {len(groups)} grupos de columnas")
        for group_id, group_data in groups.items():
            print(f"      Grupo G{group_id}: {group_data['lx_col']:.2f} x {group_data['ly_col']:.2f} m ({group_data['type']})")
    
    # Resumen de losas
    if slab_config:
        print("\n🏢 CONFIGURACIÓN DE LOSAS:")
        if slab_config['type'] == 'solid':
            print(f"  ✅ Losa maciza: espesor {slab_config['thickness']:.2f} m")
            print(f"      Peso propio: {slab_config['self_weight']:.1f} kN/m²")
        elif slab_config['type'] == 'ribbed':
            print(f"  ✅ Losa nervada: {slab_config['description']}")
            print(f"      Nervios: {slab_config['rib_width']:.2f}m cada {slab_config['rib_spacing']:.2f}m")
            print(f"      Peso propio equivalente: {slab_config['self_weight']:.1f} kN/m²")
    
    # Resumen de volados
    print("\n🏗️  CONFIGURACIÓN DE VOLADOS:")
    has_cantilevers = False
    
    if cantilever_config['front']:
        has_cantilevers = True
        front = cantilever_config['front']
        beam = front['edge_beam']
        print(f"  ✅ Volado frontal: {front['length']:.2f} m")
        print(f"      Viga de borde: {beam['width']:.2f} x {beam['height']:.2f} m")
    
    if cantilever_config['right']:
        has_cantilevers = True
        right = cantilever_config['right']
        beam = right['edge_beam']
        print(f"  ✅ Volado lateral derecho: {right['length']:.2f} m")
        print(f"      Viga de borde: {beam['width']:.2f} x {beam['height']:.2f} m")
    
    if cantilever_config['left']:
        has_cantilevers = True
        left = cantilever_config['left']
        beam = left['edge_beam']
        print(f"  ✅ Volado lateral izquierdo: {left['length']:.2f} m")
        print(f"      Viga de borde: {beam['width']:.2f} x {beam['height']:.2f} m")
    
    if not has_cantilevers:
        print("  ⭕ Sin volados configurados")
    
    print("\n" + "="*60)
    
    # Confirmación
    while True:
        try:
            confirm = input("¿Confirma esta configuración? (s/n): ").strip().lower()
            if confirm in ['s', 'si', 'y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("❌ Responda 's' para sí o 'n' para no.")
        except KeyboardInterrupt:
            print("\n⚠️ Operación cancelada")
            return False