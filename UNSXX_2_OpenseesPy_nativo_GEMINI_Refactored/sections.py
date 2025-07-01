# sections.py
# ============================================
# Este módulo gestiona la definición de las secciones transversales
# de columnas, vigas y losas. Permite configurar dimensiones y
# propiedades de los elementos estructurales, facilitando la
# modificación y expansión para futuros elementos como escaleras
# o voladizos.
#
# Características principales:
# - Múltiples tipos de materiales (concreto, acero, madera)
# - Secciones personalizables con validación
# - Cálculo automático de propiedades geométricas
# - Soporte para diferentes tipos de secciones
# - Conversión entre sistemas de unidades
# ============================================

import math
import json

class Material:
    """Clase para definir propiedades de materiales."""
    
    def __init__(self, name, E, G, nu, density, fc=None, fy=None):
        """
        Inicializa un material.
        
        Args:
            name (str): Nombre del material
            E (float): Módulo de elasticidad (kgf/cm² o MPa)
            G (float): Módulo de corte (kgf/cm² o MPa)
            nu (float): Coeficiente de Poisson
            density (float): Densidad (kg/m³)
            fc (float): Resistencia a compresión (opcional, para concreto)
            fy (float): Resistencia a fluencia (opcional, para acero)
        """
        self.name = name
        self.E = E
        self.G = G
        self.nu = nu
        self.density = density
        self.fc = fc
        self.fy = fy

def get_predefined_materials():
    """
    Retorna un diccionario con materiales predefinidos comunes.
    
    Returns:
        dict: Diccionario con materiales predefinidos
    """
    materials = {
        "concreto_f21": Material(
            name="Concreto f'c=210 kg/cm²",
            E=2040000.0,  # kgf/cm²
            G=800000.0,   # kgf/cm²
            nu=0.2,
            density=2400.0,  # kg/m³
            fc=210.0  # kg/cm²
        ),
        "concreto_f28": Material(
            name="Concreto f'c=280 kg/cm²",
            E=2550000.0,  # kgf/cm²
            G=1020000.0,  # kgf/cm²
            nu=0.2,
            density=2400.0,  # kg/m³
            fc=280.0  # kg/cm²
        ),
        "acero_a36": Material(
            name="Acero ASTM A36",
            E=20400000.0,  # kgf/cm²
            G=7850000.0,   # kgf/cm²
            nu=0.3,
            density=7850.0,  # kg/m³
            fy=2530.0  # kg/cm²
        ),
        "madera_pino": Material(
            name="Madera de Pino",
            E=100000.0,  # kgf/cm²
            G=6250.0,    # kgf/cm²
            nu=0.4,
            density=500.0,  # kg/m³
        )
    }
    return materials

def calculate_rectangular_properties(b, h):
    """
    Calcula las propiedades geométricas de una sección rectangular.
    
    Args:
        b (float): Ancho de la sección (m)
        h (float): Altura de la sección (m)
    
    Returns:
        dict: Propiedades geométricas calculadas (unidades SI: m², m⁴)
    """
    A = b * h  # m²
    Iz = (b * h**3) / 12  # m⁴
    Iy = (h * b**3) / 12  # m⁴
    J = b * h * min(b, h)**2 / 3  # m⁴
    
    return {
        "A": A,
        "Iz": Iz,
        "Iy": Iy,
        "J": J,
        "b": b,
        "h": h
    }

def calculate_circular_properties(d):
    """
    Calcula las propiedades geométricas de una sección circular.
    
    Args:
        d (float): Diámetro de la sección (m)
    
    Returns:
        dict: Propiedades geométricas calculadas (unidades SI: m², m⁴)
    """
    r = d / 2  # m
    A = math.pi * r**2  # m²
    I = (math.pi * d**4) / 64  # m⁴
    J = (math.pi * d**4) / 32  # m⁴
    
    return {
        "A": A,
        "Iz": I,
        "Iy": I,
        "J": J,
        "d": d,
        "r": r
    }

def validate_section_dimensions(dimensions, section_type):
    """
    Valida las dimensiones de una sección.
    
    Args:
        dimensions (dict): Dimensiones de la sección
        section_type (str): Tipo de sección ('rectangular', 'circular')
    
    Raises:
        ValueError: Si las dimensiones no son válidas
    """
    if section_type == "rectangular":
        if "b" not in dimensions or "h" not in dimensions:
            raise ValueError("Sección rectangular requiere 'b' y 'h'")
        if dimensions["b"] <= 0 or dimensions["h"] <= 0:
            raise ValueError("Las dimensiones deben ser positivas")
        if dimensions["b"] > 2.0 or dimensions["h"] > 2.0:
            raise ValueError("Las dimensiones son excesivamente grandes (máximo 2.0 m)")
        if dimensions["b"] < 0.10 or dimensions["h"] < 0.10:
            raise ValueError("Las dimensiones son muy pequeñas (mínimo 0.10 m)")
    elif section_type == "circular":
        if "d" not in dimensions:
            raise ValueError("Sección circular requiere 'd' (diámetro)")
        if dimensions["d"] <= 0:
            raise ValueError("El diámetro debe ser positivo")
        if dimensions["d"] > 2.0:
            raise ValueError("El diámetro es excesivamente grande (máximo 2.0 m)")
        if dimensions["d"] < 0.10:
            raise ValueError("El diámetro es muy pequeño (mínimo 0.10 m)")

def get_section_input(element_type, interactive=True):
    """
    Solicita al usuario las dimensiones de una sección o usa valores por defecto.
    
    Args:
        element_type (str): Tipo de elemento ('columna', 'viga', 'losa')
        interactive (bool): Si True, solicita entrada del usuario
    
    Returns:
        dict: Dimensiones de la sección
    """
    if not interactive:
        # Valores por defecto en metros (sistema internacional)
        defaults = {
            "columna": {"b": 0.30, "h": 0.60, "type": "rectangular"},
            "viga": {"b": 0.20, "h": 0.35, "type": "rectangular"},
            "losa": {"thickness": 0.20}  # 20 cm = 0.20 m
        }
        return defaults.get(element_type, defaults["viga"])
    
    print(f"\n--- Configuración de sección para {element_type.upper()} ---")
    
    if element_type == "losa":
        while True:
            try:
                print("NOTA: Dimensiones en metros (sistema internacional)")
                thickness = float(input("Espesor de la losa (0.10-0.50 m): "))
                if 0.10 <= thickness <= 0.50:
                    return {"thickness": thickness}
                else:
                    print("El espesor debe estar entre 0.10 y 0.50 m")
            except ValueError:
                print("Por favor ingrese un número válido")
    else:
        # Para vigas, asumir automáticamente sección rectangular
        if element_type == "viga":
            choice = 1  # Rectangular por defecto
            print("Sección rectangular seleccionada automáticamente para vigas")
        else:
            print("Tipos de sección disponibles:")
            print("1. Rectangular")
            print("2. Circular")
            
            while True:
                try:
                    choice = int(input("Seleccione el tipo de sección (1-2): "))
                    if choice in [1, 2]:
                        break
                    else:
                        print("Seleccione 1 o 2")
                except ValueError:
                    print("Por favor ingrese un número válido")
        
        if choice == 1:  # Rectangular
            while True:
                try:
                    if element_type == "columna":
                        print("NOTA: Dimensiones en metros (sistema internacional)")
                        b = float(input("Ancho de la columna en X (0.15-1.00 m): "))
                        h = float(input("Ancho de la columna en Y (0.15-1.00 m): "))
                    else:  # viga
                        print("NOTA: Dimensiones en metros (sistema internacional)")
                        b = float(input("Ancho de la viga (0.15-0.50 m): "))
                        h = float(input("Altura de la viga (0.20-1.00 m): "))
                    
                    dimensions = {"b": b, "h": h, "type": "rectangular"}
                    validate_section_dimensions(dimensions, "rectangular")
                    return dimensions
                except ValueError as e:
                    print(f"Error: {e}")
        
        else:  # Circular
            while True:
                try:
                    print("NOTA: Dimensiones en metros (sistema internacional)")
                    d = float(input("Diámetro de la sección (0.15-1.00 m): "))
                    dimensions = {"d": d, "type": "circular"}
                    validate_section_dimensions(dimensions, "circular")
                    return dimensions
                except ValueError as e:
                    print(f"Error: {e}")

def get_beam_section_configuration(interactive=True):
    """
    Solicita al usuario el tipo de configuración de vigas.
    
    Returns:
        dict: Configuración de secciones de vigas
    """
    if not interactive:
        return {
            'type': 'uniform',
            'beam_x': {"b": 0.20, "h": 0.35, "type": "rectangular"},
            'beam_y': {"b": 0.20, "h": 0.35, "type": "rectangular"}
        }
    
    print("\n=== CONFIGURACIÓN DE SECCIONES DE VIGAS ===")
    print("Opciones disponibles:")
    print("1. Todas las vigas iguales (misma sección)")
    print("2. Vigas X diferentes a vigas Y")
    
    while True:
        try:
            choice = int(input("Seleccione una opción (1-2): "))
            if choice in [1, 2]:
                break
            else:
                print("Seleccione 1 o 2")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    if choice == 1:
        # Todas las vigas iguales
        print("\n--- Configurando sección única para todas las vigas ---")
        beam_section = get_section_input("viga", True)
        return {
            'type': 'uniform',
            'beam_x': beam_section,
            'beam_y': beam_section
        }
    else:
        # Vigas X diferentes a vigas Y
        print("\n--- Configurando vigas en dirección X ---")
        beam_x_section = get_section_input("viga_x", True)
        
        print("\n--- Configurando vigas en dirección Y ---")
        beam_y_section = get_section_input("viga_y", True)
        
        return {
            'type': 'directional',
            'beam_x': beam_x_section,
            'beam_y': beam_y_section
        }

def get_section_input(element_type, interactive=True):
    """
    Solicita al usuario las dimensiones de una sección o usa valores por defecto.
    
    Args:
        element_type (str): Tipo de elemento ('columna', 'viga', 'viga_x', 'viga_y', 'losa')
        interactive (bool): Si True, solicita entrada del usuario
    
    Returns:
        dict: Dimensiones de la sección
    """
    if not interactive:
        # Valores por defecto en metros (sistema internacional)
        defaults = {
            "columna": {"b": 0.30, "h": 0.60, "type": "rectangular"},
            "viga": {"b": 0.20, "h": 0.35, "type": "rectangular"},
            "viga_x": {"b": 0.20, "h": 0.35, "type": "rectangular"},
            "viga_y": {"b": 0.20, "h": 0.35, "type": "rectangular"},
            "losa": {"thickness": 0.20}  # 20 cm = 0.20 m
        }
        return defaults.get(element_type, defaults["viga"])
    
    # Mapear nombres de elementos para mostrar
    display_names = {
        "columna": "COLUMNA",
        "viga": "VIGA",
        "viga_x": "VIGA EN DIRECCIÓN X",
        "viga_y": "VIGA EN DIRECCIÓN Y",
        "losa": "LOSA"
    }
    
    print(f"\n--- Configuración de sección para {display_names.get(element_type, element_type.upper())} ---")
    
    if element_type == "losa":
        while True:
            try:
                print("NOTA: Dimensiones en metros (sistema internacional)")
                thickness = float(input("Espesor de la losa (0.10-0.50 m): "))
                if 0.10 <= thickness <= 0.50:
                    return {"thickness": thickness}
                else:
                    print("El espesor debe estar entre 0.10 y 0.50 m")
            except ValueError:
                print("Por favor ingrese un número válido")
    else:
        # Para vigas, asumir automáticamente sección rectangular
        if element_type in ["viga", "viga_x", "viga_y"]:
            choice = 1  # Rectangular por defecto
            print("Sección rectangular seleccionada automáticamente para vigas")
        else:
            print("Tipos de sección disponibles:")
            print("1. Rectangular")
            print("2. Circular")
            
            while True:
                try:
                    choice = int(input("Seleccione el tipo de sección (1-2): "))
                    if choice in [1, 2]:
                        break
                    else:
                        print("Seleccione 1 o 2")
                except ValueError:
                    print("Por favor ingrese un número válido")
        
        if choice == 1:  # Rectangular
            while True:
                try:
                    if element_type == "columna":
                        print("NOTA: Dimensiones en metros (sistema internacional)")
                        b = float(input("Ancho de la columna en X (0.15-1.00 m): "))
                        h = float(input("Ancho de la columna en Y (0.15-1.00 m): "))
                    else:  # viga, viga_x, viga_y
                        print("NOTA: Dimensiones en metros (sistema internacional)")
                        element_display = display_names.get(element_type, "viga").lower()
                        b = float(input(f"Ancho de la {element_display} (0.15-0.50 m): "))
                        h = float(input(f"Altura de la {element_display} (0.20-1.00 m): "))
                    
                    dimensions = {"b": b, "h": h, "type": "rectangular"}
                    validate_section_dimensions(dimensions, "rectangular")
                    return dimensions
                except ValueError as e:
                    print(f"Error: {e}")
        
        else:  # Circular
            while True:
                try:
                    print("NOTA: Dimensiones en metros (sistema internacional)")
                    d = float(input("Diámetro de la sección (0.15-1.00 m): "))
                    dimensions = {"d": d, "type": "circular"}
                    validate_section_dimensions(dimensions, "circular")
                    return dimensions
                except ValueError as e:
                    print(f"Error: {e}")

def define_sections(interactive=True, material_choice=None, skip_columns=False):
    """
    Define las propiedades de los materiales y las secciones transversales
    de columnas, vigas y losas con opciones personalizables.

    Args:
        interactive (bool): Si True, solicita entrada del usuario para personalización
        material_choice (str): Clave del material predefinido (opcional)
        skip_columns (bool): Si True, omite la configuración de columnas

    Returns:
        dict: Un diccionario con todas las propiedades de las secciones.
    """
    print("\n=== DEFINICIÓN DE MATERIALES Y SECCIONES ===")
    
    # Selección de material
    materials = get_predefined_materials()
    
    if interactive and material_choice is None:
        print("\nMateriales disponibles:")
        for i, (key, material) in enumerate(materials.items(), 1):
            print(f"{i}. {material.name}")
        
        while True:
            try:
                choice = int(input("Seleccione el material (1-{}): ".format(len(materials))))
                if 1 <= choice <= len(materials):
                    material_key = list(materials.keys())[choice - 1]
                    break
                else:
                    print(f"Seleccione un número entre 1 y {len(materials)}")
            except ValueError:
                print("Por favor ingrese un número válido")
    else:
        material_key = material_choice if material_choice in materials else "concreto_f21"
    
    selected_material = materials[material_key]
    print(f"\nMaterial seleccionado: {selected_material.name}")
    print(f"  - Módulo de elasticidad (E): {selected_material.E:,.0f} kgf/cm²")
    print(f"  - Módulo de corte (G): {selected_material.G:,.0f} kgf/cm²")
    print(f"  - Coeficiente de Poisson (ν): {selected_material.nu}")
    print(f"  - Densidad: {selected_material.density} kg/m³")
    
    # Configuración de secciones
    if interactive and not skip_columns:
        print("\n¿Desea personalizar las dimensiones de las secciones?")
        customize = input("Ingrese 's' para personalizar o cualquier otra tecla para usar valores por defecto: ").lower().strip()
        interactive_sections = customize in ['s', 'si', 'sí', 'y', 'yes']
    else:
        interactive_sections = False
    
    # Obtener dimensiones de secciones
    if skip_columns:
        print("\n  Las columnas ya fueron configuradas en configuraciones avanzadas.")
        print("  Configurando solo vigas y losas...")
        # Usar dimensiones por defecto para columnas
        col_dimensions = {"b": 0.30, "h": 0.60, "type": "rectangular"}
    else:
        col_dimensions = get_section_input("columna", interactive_sections)
    
    # Configuración de vigas (SIEMPRE solicitar en modo interactivo)
    beam_config = get_beam_section_configuration(interactive)
    slab_dimensions = get_section_input("losa", interactive_sections)
    
    # Calcular propiedades geométricas
    if col_dimensions.get("type") == "circular":
        col_properties = calculate_circular_properties(col_dimensions["d"])
        col_properties.update({"type": "circular"})
    else:
        col_properties = calculate_rectangular_properties(col_dimensions["b"], col_dimensions["h"])
        col_properties.update({"type": "rectangular"})
    
    # Calcular propiedades de vigas X
    beam_x_dimensions = beam_config['beam_x']
    if beam_x_dimensions.get("type") == "circular":
        beam_x_properties = calculate_circular_properties(beam_x_dimensions["d"])
        beam_x_properties.update({"type": "circular"})
    else:
        beam_x_properties = calculate_rectangular_properties(beam_x_dimensions["b"], beam_x_dimensions["h"])
        beam_x_properties.update({"type": "rectangular"})
    
    # Calcular propiedades de vigas Y
    beam_y_dimensions = beam_config['beam_y']
    if beam_y_dimensions.get("type") == "circular":
        beam_y_properties = calculate_circular_properties(beam_y_dimensions["d"])
        beam_y_properties.update({"type": "circular"})
    else:
        beam_y_properties = calculate_rectangular_properties(beam_y_dimensions["b"], beam_y_dimensions["h"])
        beam_y_properties.update({"type": "rectangular"})
    
    # Mostrar resumen de propiedades calculadas
    print("\n=== PROPIEDADES GEOMÉTRICAS CALCULADAS ===")
    
    # Convertir a cm para mostrar dimensiones más legibles
    if col_properties["type"] == "rectangular":
        print(f"Columnas ({col_properties['b']*100:.0f} x {col_properties['h']*100:.0f} cm):")
    else:
        print(f"Columnas (Ø {col_properties['d']*100:.0f} cm):")
    print(f"  - Área: {col_properties['A']*10000:.0f} cm²")  # m² a cm²
    print(f"  - Iz: {col_properties['Iz']*100000000:.0f} cm⁴")  # m⁴ a cm⁴
    print(f"  - Iy: {col_properties['Iy']*100000000:.0f} cm⁴")  # m⁴ a cm⁴
    print(f"  - J: {col_properties['J']*100000000:.0f} cm⁴")   # m⁴ a cm⁴
    
    # Mostrar configuración de vigas
    if beam_config['type'] == 'uniform':
        print(f"\nVigas (TODAS IGUALES):")
        if beam_x_properties["type"] == "rectangular":
            print(f"  Dimensiones: {beam_x_properties['b']*100:.0f} x {beam_x_properties['h']*100:.0f} cm")
        else:
            print(f"  Dimensiones: Ø {beam_x_properties['d']*100:.0f} cm")
        print(f"  - Área: {beam_x_properties['A']*10000:.0f} cm²")
        print(f"  - Iz: {beam_x_properties['Iz']*100000000:.0f} cm⁴")
        print(f"  - Iy: {beam_x_properties['Iy']*100000000:.0f} cm⁴")
        print(f"  - J: {beam_x_properties['J']*100000000:.0f} cm⁴")
    else:
        print(f"\nVigas X (dirección X):")
        if beam_x_properties["type"] == "rectangular":
            print(f"  Dimensiones: {beam_x_properties['b']*100:.0f} x {beam_x_properties['h']*100:.0f} cm")
        else:
            print(f"  Dimensiones: Ø {beam_x_properties['d']*100:.0f} cm")
        print(f"  - Área: {beam_x_properties['A']*10000:.0f} cm²")
        print(f"  - Iz: {beam_x_properties['Iz']*100000000:.0f} cm⁴")
        print(f"  - Iy: {beam_x_properties['Iy']*100000000:.0f} cm⁴")
        print(f"  - J: {beam_x_properties['J']*100000000:.0f} cm⁴")
        
        print(f"\nVigas Y (dirección Y):")
        if beam_y_properties["type"] == "rectangular":
            print(f"  Dimensiones: {beam_y_properties['b']*100:.0f} x {beam_y_properties['h']*100:.0f} cm")
        else:
            print(f"  Dimensiones: Ø {beam_y_properties['d']*100:.0f} cm")
        print(f"  - Área: {beam_y_properties['A']*10000:.0f} cm²")
        print(f"  - Iz: {beam_y_properties['Iz']*100000000:.0f} cm⁴")
        print(f"  - Iy: {beam_y_properties['Iy']*100000000:.0f} cm⁴")
        print(f"  - J: {beam_y_properties['J']*100000000:.0f} cm⁴")
    
    print(f"\nLosas (Espesor: {slab_dimensions['thickness']*100:.0f} cm)")
    print("=" * 60)
    
    # Compilar diccionario de retorno
    result = {
        # Propiedades del material
        "E": selected_material.E,
        "G": selected_material.G,
        "nu": selected_material.nu,
        "density": selected_material.density,
        "material_name": selected_material.name,
        
        # Propiedades de columnas
        "A_col": col_properties["A"],
        "Iz_col": col_properties["Iz"],
        "Iy_col": col_properties["Iy"],
        "J_col": col_properties["J"],
        "col_type": col_properties["type"],
        
        # Propiedades de vigas X
        "A_viga_x": beam_x_properties["A"],
        "Iz_viga_x": beam_x_properties["Iz"],
        "Iy_viga_x": beam_x_properties["Iy"],
        "J_viga_x": beam_x_properties["J"],
        "beam_x_type": beam_x_properties["type"],
        
        # Propiedades de vigas Y
        "A_viga_y": beam_y_properties["A"],
        "Iz_viga_y": beam_y_properties["Iz"],
        "Iy_viga_y": beam_y_properties["Iy"],
        "J_viga_y": beam_y_properties["J"],
        "beam_y_type": beam_y_properties["type"],
        
        # Configuración de vigas
        "beam_config_type": beam_config['type'],
        
        # Propiedades heredadas (para compatibilidad)
        "A_viga": beam_x_properties["A"],  # Por defecto usa vigas X
        "Iz_viga": beam_x_properties["Iz"],
        "Iy_viga": beam_x_properties["Iy"],
        "J_viga": beam_x_properties["J"],
        "beam_type": beam_x_properties["type"],
        
        # Dimensiones de losas
        "slab_thickness": slab_dimensions["thickness"],
    }
    
    # Agregar dimensiones específicas según el tipo
    if col_properties["type"] == "rectangular":
        result.update({
            "lx_col": col_properties["b"],
            "ly_col": col_properties["h"]
        })
    else:
        result.update({
            "d_col": col_properties["d"]
        })
    
    # Dimensiones de vigas X
    if beam_x_properties["type"] == "rectangular":
        result.update({
            "b_viga_x": beam_x_properties["b"],
            "h_viga_x": beam_x_properties["h"]
        })
    else:
        result.update({
            "d_viga_x": beam_x_properties["d"]
        })
    
    # Dimensiones de vigas Y
    if beam_y_properties["type"] == "rectangular":
        result.update({
            "b_viga_y": beam_y_properties["b"],
            "h_viga_y": beam_y_properties["h"]
        })
    else:
        result.update({
            "d_viga_y": beam_y_properties["d"]
        })
    
    # Dimensiones heredadas (para compatibilidad)
    if beam_x_properties["type"] == "rectangular":
        result.update({
            "b_viga": beam_x_properties["b"],
            "h_viga": beam_x_properties["h"]
        })
    else:
        result.update({
            "d_viga": beam_x_properties["d"]
        })
    
    return result

def save_sections_config(sections_data, filename=None):
    """
    Guarda la configuración de secciones en un archivo JSON.
    
    Args:
        sections_data (dict): Datos de secciones a guardar
        filename (str): Nombre del archivo (opcional)
    """
    if filename is None:
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sections_config_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sections_data, f, indent=2, ensure_ascii=False)
        print(f"Configuración de secciones guardada en: {filename}")
    except Exception as e:
        print(f"Error al guardar la configuración de secciones: {e}")

def load_sections_config(filename):
    """
    Carga una configuración de secciones desde un archivo JSON.
    
    Args:
        filename (str): Nombre del archivo a cargar
    
    Returns:
        dict: Datos de secciones cargados
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# --- Puntos para escalar el código: Secciones ---
# - Implementar secciones de acero laminado (perfiles I, H, C, L)
# - Añadir secciones compuestas (acero-concreto)
# - Implementar secciones de madera (dimensiones comerciales)
# - Añadir verificación de capacidades según normativas
# - Implementar secciones optimizadas automáticamente
# - Añadir soporte para secciones no prismáticas
# - Implementar materiales compuestos y de alta resistencia
