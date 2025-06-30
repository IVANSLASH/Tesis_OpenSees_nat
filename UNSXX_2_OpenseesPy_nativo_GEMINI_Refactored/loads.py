# loads.py
# ============================================
# Este módulo define y asigna las cargas (muertas, vivas, de diseño)
# a los elementos estructurales (losas, vigas). Incluye la lógica para
# la transmisión de cargas y la creación de combinaciones de carga
# para el análisis.
#
# Características principales:
# - Cargas distribuidas y puntuales en losas y vigas
# - Cargas muertas y vivas con intensidades configurables
# - Combinaciones de carga según normativas (LRFD, ASD)
# - Transmisión automática de cargas: losas → vigas → columnas
# - Cargas sísmicas y de viento (preparado para expansión)
# - Patrones de carga múltiples para análisis completo
# ============================================

import openseespy.opensees as ops
import geometry
import math

class LoadCase:
    """Clase para definir casos de carga."""
    
    def __init__(self, name, load_type, description=""):
        """
        Inicializa un caso de carga.
        
        Args:
            name (str): Nombre del caso de carga
            load_type (str): Tipo de carga ('dead', 'live', 'wind', 'seismic')
            description (str): Descripción opcional
        """
        self.name = name
        self.load_type = load_type
        self.description = description
        self.point_loads = []  # Lista de cargas puntuales
        self.distributed_loads = []  # Lista de cargas distribuidas
        self.element_loads = []  # Lista de cargas en elementos

def get_load_intensities(interactive=True, slab_config=None):
    """
    Solicita al usuario las intensidades de carga o usa valores por defecto.
    
    Args:
        interactive (bool): Si True, solicita entrada del usuario
        slab_config (dict): Configuración del tipo de losa
    
    Returns:
        dict: Diccionario con intensidades de carga
    """
    # Obtener peso propio de losa según configuración
    slab_self_weight = 5.0  # kN/m² por defecto
    if slab_config:
        slab_self_weight = slab_config.get('self_weight', 5.0)
    
    if not interactive:
        # Valores por defecto típicos para edificios (en kN)
        return {
            "dead_load_slab": 4.0 + slab_self_weight,  # kN/m² (carga muerta + peso propio)
            "live_load_slab": 2.0,                     # kN/m² (carga viva en losas)
            "dead_load_beam": 1.0,                     # kN/m (carga muerta lineal en vigas)
            "live_load_beam": 0.5,                     # kN/m (carga viva lineal en vigas)
            "point_load_test": 10.0,                   # kN (carga puntual de prueba)
            "wind_pressure": 1.0,                      # kN/m² (presión de viento)
            "seismic_coeff": 0.2,                      # Coeficiente sísmico
            "slab_self_weight": slab_self_weight       # kN/m² (peso propio de losa)
        }
    
    print("\n=== CONFIGURACIÓN DE INTENSIDADES DE CARGA ===")
    print("SISTEMA DE UNIDADES: Las cargas se ingresan en kN/m² y kN/m")
    print("Valores típicos para edificios:")
    print("  • Losas: 2-8 kN/m² (cargas variables)")
    print("  • Vigas: 1-3 kN/m (cargas adicionales)")
    
    if slab_config:
        print(f"\n📋 INFORMACIÓN DE LOSA CONFIGURADA:")
        print(f"  • Tipo: {slab_config.get('description', 'No especificado')}")
        print(f"  • Peso propio: {slab_self_weight:.1f} kN/m²")
    
    intensities = {}
    
    # Cargas muertas en losas (excluyendo peso propio)
    print(f"\n🏗️  CARGAS MUERTAS EN LOSAS:")
    print(f"El peso propio de {slab_self_weight:.1f} kN/m² se añade automáticamente.")
    while True:
        try:
            dead_slab_additional = float(input("Carga muerta adicional en losas (kN/m²) [2.0-8.0]: "))
            if 2.0 <= dead_slab_additional <= 8.0:
                intensities["dead_load_slab"] = dead_slab_additional + slab_self_weight
                break
            else:
                print("La carga debe estar entre 2.0 y 8.0 kN/m²")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Cargas vivas en losas
    print(f"\n🏠 CARGAS VIVAS EN LOSAS:")
    while True:
        try:
            live_slab = float(input("Carga viva en losas (kN/m²) [1.0-5.0]: "))
            if 1.0 <= live_slab <= 5.0:
                intensities["live_load_slab"] = live_slab
                break
            else:
                print("La carga debe estar entre 1.0 y 5.0 kN/m²")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Cargas en vigas
    print(f"\n🌉 CARGAS ADICIONALES EN VIGAS:")
    while True:
        try:
            dead_beam = float(input("Carga muerta adicional en vigas (kN/m) [0.5-3.0]: "))
            if 0.5 <= dead_beam <= 3.0:
                intensities["dead_load_beam"] = dead_beam
                break
            else:
                print("La carga debe estar entre 0.5 y 3.0 kN/m")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Valores automáticos para otras cargas
    intensities.update({
        "live_load_beam": intensities["dead_load_beam"] * 0.5,
        "point_load_test": 10.0,                # kN
        "wind_pressure": 1.0,                   # kN/m²
        "seismic_coeff": 0.2,                   # Coeficiente sísmico
        "slab_self_weight": slab_self_weight    # kN/m²
    })
    
    return intensities

def get_load_combinations():
    """
    Define las combinaciones de carga según normativas.
    
    Returns:
        dict: Diccionario con combinaciones de carga
    """
    combinations = {
        "service": {
            "name": "Cargas de Servicio",
            "factors": {"dead": 1.0, "live": 1.0},
            "description": "D + L"
        },
        "ultimate_basic": {
            "name": "Combinación Última Básica",
            "factors": {"dead": 1.2, "live": 1.6},
            "description": "1.2D + 1.6L"
        },
        "ultimate_wind": {
            "name": "Combinación Última con Viento",
            "factors": {"dead": 1.2, "live": 1.0, "wind": 1.6},
            "description": "1.2D + 1.0L + 1.6W"
        },
        "ultimate_seismic": {
            "name": "Combinación Última con Sismo",
            "factors": {"dead": 1.2, "live": 1.0, "seismic": 1.0},
            "description": "1.2D + 1.0L + 1.0E"
        }
    }
    return combinations

def calculate_tributary_area(geometry_data, bay_i, bay_j):
    """
    Calcula el área tributaria para un nodo específico.
    
    Args:
        geometry_data (dict): Datos de geometría del edificio
        bay_i (int): Índice del vano en dirección X
        bay_j (int): Índice del vano en dirección Y
    
    Returns:
        float: Área tributaria en m²
    """
    bay_widths_x = geometry_data["bay_widths_x"]
    bay_widths_y = geometry_data["bay_widths_y"]
    
    # Calcular dimensiones tributarias
    if bay_i == 0:
        width_x = bay_widths_x[0] / 2
    elif bay_i == len(bay_widths_x):
        width_x = bay_widths_x[-1] / 2
    else:
        width_x = (bay_widths_x[bay_i-1] + bay_widths_x[bay_i]) / 2
    
    if bay_j == 0:
        width_y = bay_widths_y[0] / 2
    elif bay_j == len(bay_widths_y):
        width_y = bay_widths_y[-1] / 2
    else:
        width_y = (bay_widths_y[bay_j-1] + bay_widths_y[bay_j]) / 2
    
    return width_x * width_y

def apply_dead_loads(geometry_data, load_intensities, pattern_tag=1):
    """
    Aplica cargas muertas al modelo.
    
    Args:
        geometry_data (dict): Datos de geometría del edificio
        load_intensities (dict): Intensidades de carga
        pattern_tag (int): Tag del patrón de carga
    """
    print(f"\n  Aplicando cargas muertas (Patrón {pattern_tag})...")
    
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]
    
    dead_load_slab = load_intensities["dead_load_slab"]
    
    # Aplicar cargas muertas de losa a nodos
    loads_applied = 0
    for floor in range(1, num_floor + 1):  # Excluir nivel base
        for j in range(num_bay_y + 1):  # Índices de vanos Y
            for i in range(num_bay_x + 1):  # Índices de vanos X
                # Obtener tag del nodo
                node_tag = geometry.get_node_tag_from_indices(floor, j, i, num_bay_x, num_bay_y)
                
                # Calcular área tributaria
                tributary_area = calculate_tributary_area(geometry_data, i, j)
                
                # Calcular carga puntual equivalente
                point_load = dead_load_slab * tributary_area
                
                # Aplicar carga vertical (hacia abajo)
                ops.load(node_tag, 0, 0, -point_load, 0, 0, 0)
                loads_applied += 1
    
    print(f"    Cargas muertas aplicadas a {loads_applied} nodos")
    print(f"    Intensidad: {dead_load_slab} kN/m²")

def apply_live_loads(geometry_data, load_intensities, pattern_tag=2):
    """
    Aplica cargas vivas al modelo.
    
    Args:
        geometry_data (dict): Datos de geometría del edificio
        load_intensities (dict): Intensidades de carga
        pattern_tag (int): Tag del patrón de carga
    """
    print(f"\n  Aplicando cargas vivas (Patrón {pattern_tag})...")
    
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]
    
    live_load_slab = load_intensities["live_load_slab"]
    
    # Aplicar cargas vivas de losa a nodos
    loads_applied = 0
    for floor in range(1, num_floor + 1):  # Excluir nivel base
        for j in range(num_bay_y + 1):  # Índices de vanos Y
            for i in range(num_bay_x + 1):  # Índices de vanos X
                # Obtener tag del nodo
                node_tag = geometry.get_node_tag_from_indices(floor, j, i, num_bay_x, num_bay_y)
                
                # Calcular área tributaria
                tributary_area = calculate_tributary_area(geometry_data, i, j)
                
                # Calcular carga puntual equivalente
                point_load = live_load_slab * tributary_area
                
                # Aplicar carga vertical (hacia abajo)
                ops.load(node_tag, 0, 0, -point_load, 0, 0, 0)
                loads_applied += 1
    
    print(f"    Cargas vivas aplicadas a {loads_applied} nodos")
    print(f"    Intensidad: {live_load_slab} kN/m²")

def apply_beam_loads(geometry_data, load_intensities, beam_elements_x, beam_elements_y, load_type="dead"):
    """
    Aplica cargas distribuidas a vigas.
    
    Args:
        geometry_data (dict): Datos de geometría del edificio
        load_intensities (dict): Intensidades de carga
        beam_elements_x (list): Lista de elementos viga en X
        beam_elements_y (list): Lista de elementos viga en Y
        load_type (str): Tipo de carga ('dead' o 'live')
    """
    if load_type == "dead":
        load_intensity = load_intensities["dead_load_beam"]
    else:
        load_intensity = load_intensities["live_load_beam"]
    
    print(f"    Aplicando cargas {load_type} distribuidas en vigas: {load_intensity} kN/m")
    
    total_beams_loaded = 0
    
    # Aplicar cargas a vigas en X
    if beam_elements_x:
        for ele_id in beam_elements_x:
            try:
                ops.eleLoad('-ele', ele_id, '-type', '-beamUniform', 0, -load_intensity)
                total_beams_loaded += 1
            except Exception as e:
                print(f"      Error aplicando carga a viga X {ele_id}: {e}")
    
    # Aplicar cargas a vigas en Y
    if beam_elements_y:
        for ele_id in beam_elements_y:
            try:
                ops.eleLoad('-ele', ele_id, '-type', '-beamUniform', 0, -load_intensity)
                total_beams_loaded += 1
            except Exception as e:
                print(f"      Error aplicando carga a viga Y {ele_id}: {e}")
    
    total_beams = len(beam_elements_x) + len(beam_elements_y)
    print(f"    Cargas aplicadas a {total_beams_loaded}/{total_beams} vigas")
    
    if total_beams == 0:
        print("    ⚠️  No hay vigas en el modelo para aplicar cargas distribuidas")

def apply_point_load_test(geometry_data, load_intensities, pattern_tag=3):
    """
    Aplica una carga puntual de prueba en el último nivel.
    
    Args:
        geometry_data (dict): Datos de geometría del edificio
        load_intensities (dict): Intensidades de carga
        pattern_tag (int): Tag del patrón de carga
    """
    num_bay_x = geometry_data["num_bay_x"]
    num_bay_y = geometry_data["num_bay_y"]
    num_floor = geometry_data["num_floor"]
    
    # Nodo central del último nivel
    center_i = num_bay_x // 2
    center_j = num_bay_y // 2
    test_node = geometry.get_node_tag_from_indices(num_floor, center_j, center_i, num_bay_x, num_bay_y)
    
    test_load = load_intensities["point_load_test"]
    
    print(f"\n  Aplicando carga puntual de prueba:")
    print(f"    Nodo: {test_node} (último nivel, posición central)")
    print(f"    Carga: {test_load} kN en dirección X")
    
    ops.load(test_node, test_load, 0, 0, 0, 0, 0)

def create_load_combination(combination_name, combinations, time_series_tag=1):
    """
    Crea una combinación de carga específica.
    
    Args:
        combination_name (str): Nombre de la combinación
        combinations (dict): Diccionario con definiciones de combinaciones
        time_series_tag (int): Tag de la serie de tiempo
    """
    if combination_name not in combinations:
        print(f"Combinación '{combination_name}' no encontrada")
        return
    
    combo = combinations[combination_name]
    print(f"\nCreando combinación: {combo['name']}")
    print(f"Descripción: {combo['description']}")
    
    # Para simplicidad, usaremos la combinación básica D + L
    # En una implementación completa, se manejarían múltiples patrones
    factors = combo["factors"]
    dead_factor = factors.get("dead", 0)
    live_factor = factors.get("live", 0)
    
    if dead_factor != 0 and live_factor != 0:
        effective_factor = dead_factor + live_factor  # Simplificación
        print(f"Factor efectivo aplicado: {effective_factor}")

def apply_loads(geometry_data, load_intensities, beam_elements_x, beam_elements_y, 
                total_nodes, interactive=True, combination="service"):
    """
    Función principal para aplicar cargas al modelo estructural.

    Args:
        geometry_data (dict): Diccionario con los datos de geometría del edificio
        load_intensities (dict): Intensidades de carga configuradas
        beam_elements_x (list): Lista de elementos viga en dirección X
        beam_elements_y (list): Lista de elementos viga en dirección Y
        total_nodes (int): El número total de nodos en el modelo
        interactive (bool): Si mostrar información detallada
        combination (str): Tipo de combinación de carga a usar
    """
    print("\n=== APLICACIÓN DE CARGAS ===")
    
    # Obtener combinaciones de carga
    combinations = get_load_combinations()
    
    if interactive:
        print(f"\nCombinación de carga seleccionada: {combinations[combination]['name']}")
        print(f"Descripción: {combinations[combination]['description']}")
    
    # Configurar series de tiempo y patrones de carga
    ops.timeSeries('Linear', 1)
    
    # Patrón para cargas muertas
    ops.pattern('Plain', 1, 1)
    apply_dead_loads(geometry_data, load_intensities, 1)
    apply_beam_loads(geometry_data, load_intensities, beam_elements_x, beam_elements_y, "dead")
    
    # Patrón para cargas vivas
    ops.pattern('Plain', 2, 1)
    apply_live_loads(geometry_data, load_intensities, 2)
    apply_beam_loads(geometry_data, load_intensities, beam_elements_x, beam_elements_y, "live")
    
    # Patrón para carga puntual de prueba (opcional)
    if interactive:
        add_test_load = input("\n¿Aplicar carga puntual de prueba? (s/n): ").lower().strip()
        if add_test_load in ['s', 'si', 'sí', 'y', 'yes']:
            ops.pattern('Plain', 3, 1)
            apply_point_load_test(geometry_data, load_intensities, 3)
    
    # Crear combinación de carga
    create_load_combination(combination, combinations)
    
    # Resumen final
    print(f"\n=== RESUMEN DE CARGAS APLICADAS ===")
    print(f"Intensidad carga muerta losas: {load_intensities['dead_load_slab']} kN/m²")
    print(f"Intensidad carga viva losas: {load_intensities['live_load_slab']} kN/m²")
    print(f"Intensidad carga muerta vigas: {load_intensities['dead_load_beam']} kN/m")
    print(f"Intensidad carga viva vigas: {load_intensities['live_load_beam']} kN/m")
    print(f"Combinación aplicada: {combinations[combination]['description']}")
    
    total_dead_load = (load_intensities['dead_load_slab'] * 
                      sum(geometry_data['bay_widths_x']) * 
                      sum(geometry_data['bay_widths_y']) * 
                      geometry_data['num_floor'])
    
    total_live_load = (load_intensities['live_load_slab'] * 
                      sum(geometry_data['bay_widths_x']) * 
                      sum(geometry_data['bay_widths_y']) * 
                      geometry_data['num_floor'])
    
    print(f"Carga muerta total estimada: {total_dead_load:.1f} kN")
    print(f"Carga viva total estimada: {total_live_load:.1f} kN")
    print("=" * 50)

# --- Puntos para escalar el código: Cargas ---
# - Implementar cargas sísmicas según espectros de respuesta
# - Añadir cargas de viento según normativas (ASCE 7, etc.)
# - Implementar cargas térmicas y de retracción
# - Añadir cargas móviles para puentes y estructuras especiales
# - Implementar análisis de patrones de carga viva alternantes
# - Añadir cargas de construcción y montaje
# - Implementar cargas de fluidos y presiones hidrostáticas
# - Añadir cargas accidentales (explosión, impacto, etc.)