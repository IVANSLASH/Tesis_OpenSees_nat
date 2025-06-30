# input_data.py
# ============================================
# Este módulo gestiona la entrada de datos del usuario para la geometría
# del edificio (número de niveles, vanos, longitudes, alturas) y otras
# configuraciones iniciales. Incluye funciones para solicitar y validar
# los datos, facilitando la adaptación a futuras interfaces de entrada.
#
# Características principales:
# - Validación robusta de datos de entrada
# - Soporte para entrada interactiva y automática
# - Configuración de parámetros de discretización de losas
# - Validaciones de rangos y tipos de datos
# - Opción de cargar configuraciones predefinidas
# ============================================

import json
import os

def validate_positive_number(value, name, min_value=0.1, max_value=100):
    """
    Valida que un valor sea un número positivo dentro de un rango.
    
    Args:
        value: El valor a validar
        name: Nombre del parámetro para mensajes de error
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
    
    Returns:
        float: El valor validado
    
    Raises:
        ValueError: Si el valor no es válido
    """
    try:
        num_value = float(value)
        if num_value < min_value or num_value > max_value:
            raise ValueError(f"{name} debe estar entre {min_value} y {max_value} metros")
        return num_value
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(f"{name} debe ser un número válido")
        raise e

def validate_positive_integer(value, name, min_value=1, max_value=20):
    """
    Valida que un valor sea un entero positivo dentro de un rango.
    
    Args:
        value: El valor a validar
        name: Nombre del parámetro para mensajes de error
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
    
    Returns:
        int: El valor validado
    
    Raises:
        ValueError: Si el valor no es válido
    """
    try:
        int_value = int(value)
        if int_value < min_value or int_value > max_value:
            raise ValueError(f"{name} debe estar entre {min_value} y {max_value}")
        return int_value
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError(f"{name} debe ser un número entero válido")
        raise e

def get_input_with_validation(prompt, validation_func, *args):
    """
    Solicita entrada del usuario con validación automática.
    
    Args:
        prompt: Mensaje a mostrar al usuario
        validation_func: Función de validación a aplicar
        *args: Argumentos adicionales para la función de validación
    
    Returns:
        El valor validado
    """
    while True:
        try:
            user_input = input(prompt)
            return validation_func(user_input, *args)
        except ValueError as e:
            print(f"Error: {e}. Por favor, intente nuevamente.")

def get_building_geometry_data(interactive=True, config_file=None):
    """
    Solicita al usuario los parámetros geométricos del edificio con validaciones.

    Args:
        interactive (bool): Si True, solicita datos interactivamente. Si False, usa valores por defecto.
        config_file (str): Ruta a archivo de configuración JSON (opcional).

    Returns:
        dict: Un diccionario con los datos de geometría ingresados y validados.
    """
    print("=== CONFIGURACIÓN GEOMÉTRICA DEL EDIFICIO ===")
    
    # Cargar configuración desde archivo si se proporciona
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                print(f"Configuración cargada desde {config_file}")
                return validate_geometry_data(config_data)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            print("Continuando con entrada manual...")

    if not interactive:
        print("Usando configuración por defecto para pruebas rápidas...")
        return get_default_geometry_data()

    # Entrada interactiva con validaciones
    print("\nNota: Los valores deben estar en metros y ser positivos.")
    print("Rangos recomendados:")
    print("- Vanos: 1-20 por dirección")
    print("- Pisos: 1-20")
    print("- Longitudes de vanos: 3.0-15.0 metros")
    print("- Alturas de pisos: 2.5-5.0 metros\n")

    num_bay_x = get_input_with_validation(
        "Ingrese el número de vanos en dirección X (1-20): ",
        validate_positive_integer, "Número de vanos X", 1, 20
    )
    
    num_bay_y = get_input_with_validation(
        "Ingrese el número de vanos en dirección Y (1-20): ",
        validate_positive_integer, "Número de vanos Y", 1, 20
    )
    
    num_floor = get_input_with_validation(
        "Ingrese el número de pisos (1-20): ",
        validate_positive_integer, "Número de pisos", 1, 20
    )

    bay_widths_x = []
    print(f"\n--- Longitudes de {num_bay_x} vanos en dirección X ---")
    for i in range(num_bay_x):
        longitud = get_input_with_validation(
            f"Longitud del vano {i+1} en X (3.0-15.0 metros): ",
            validate_positive_number, f"Longitud vano X{i+1}", 3.0, 15.0
        )
        bay_widths_x.append(longitud)

    bay_widths_y = []
    print(f"\n--- Longitudes de {num_bay_y} vanos en dirección Y ---")
    for j in range(num_bay_y):
        longitud = get_input_with_validation(
            f"Longitud del vano {j+1} en Y (3.0-15.0 metros): ",
            validate_positive_number, f"Longitud vano Y{j+1}", 3.0, 15.0
        )
        bay_widths_y.append(longitud)

    story_heights = []
    print(f"\n--- Alturas de {num_floor} pisos ---")
    for k in range(num_floor):
        altura = get_input_with_validation(
            f"Altura del piso {k+1} (2.5-5.0 metros): ",
            validate_positive_number, f"Altura piso {k+1}", 2.5, 5.0
        )
        story_heights.append(altura)

    # Configuración de discretización de losas
    print("\n--- Configuración de discretización de losas ---")
    print("Número de divisiones por vano para elementos shell de losa.")
    print("Más divisiones = mayor precisión pero más tiempo de cálculo.")
    
    mesh_density = get_input_with_validation(
        "Divisiones por vano para losas (1-10, recomendado: 2-4): ",
        validate_positive_integer, "Densidad de malla", 1, 10
    )

    geometry_data = {
        "num_bay_x": num_bay_x,
        "num_bay_y": num_bay_y,
        "num_floor": num_floor,
        "bay_widths_x": bay_widths_x,
        "bay_widths_y": bay_widths_y,
        "story_heights": story_heights,
        "mesh_density": mesh_density,
    }

    # Validación final y resumen
    print("\n=== RESUMEN DE CONFIGURACIÓN ===")
    print(f"Número de vanos X: {num_bay_x}")
    print(f"Número de vanos Y: {num_bay_y}")
    print(f"Número de pisos: {num_floor}")
    print(f"Longitudes vanos X: {bay_widths_x} metros")
    print(f"Longitudes vanos Y: {bay_widths_y} metros")
    print(f"Alturas de pisos: {story_heights} metros")
    print(f"Densidad de malla de losas: {mesh_density} divisiones por vano")
    print(f"Dimensiones totales del edificio:")
    print(f"  - Ancho X: {sum(bay_widths_x):.2f} metros")
    print(f"  - Ancho Y: {sum(bay_widths_y):.2f} metros")
    print(f"  - Altura total: {sum(story_heights):.2f} metros")

    # Pregunta si desea guardar la configuración
    save_config = input("\n¿Desea guardar esta configuración en un archivo? (s/n): ").lower().strip()
    if save_config in ['s', 'si', 'sí', 'y', 'yes']:
        save_geometry_config(geometry_data)

    return geometry_data

def get_default_geometry_data():
    """
    Retorna una configuración por defecto para pruebas rápidas.
    
    Returns:
        dict: Configuración por defecto
    """
    return {
        "num_bay_x": 3,
        "num_bay_y": 3,
        "num_floor": 3,
        "bay_widths_x": [5.0, 6.0, 5.0],
        "bay_widths_y": [4.0, 5.0, 4.0],
        "story_heights": [3.0, 3.0, 3.0],
        "mesh_density": 2,
    }

def validate_geometry_data(data):
    """
    Valida un diccionario de datos de geometría.
    
    Args:
        data (dict): Diccionario con datos de geometría
    
    Returns:
        dict: Datos validados
    
    Raises:
        ValueError: Si los datos no son válidos
    """
    required_keys = ["num_bay_x", "num_bay_y", "num_floor", "bay_widths_x", "bay_widths_y", "story_heights"]
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Clave requerida '{key}' no encontrada en los datos")
    
    if len(data["bay_widths_x"]) != data["num_bay_x"]:
        raise ValueError("El número de longitudes de vanos X no coincide con num_bay_x")
    
    if len(data["bay_widths_y"]) != data["num_bay_y"]:
        raise ValueError("El número de longitudes de vanos Y no coincide con num_bay_y")
    
    if len(data["story_heights"]) != data["num_floor"]:
        raise ValueError("El número de alturas de pisos no coincide con num_floor")
    
    # Añadir mesh_density si no existe
    if "mesh_density" not in data:
        data["mesh_density"] = 2
    
    return data

def save_geometry_config(geometry_data, filename=None):
    """
    Guarda la configuración de geometría en un archivo JSON.
    
    Args:
        geometry_data (dict): Datos de geometría a guardar
        filename (str): Nombre del archivo (opcional)
    """
    if filename is None:
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"building_config_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(geometry_data, f, indent=2, ensure_ascii=False)
        print(f"Configuración guardada en: {filename}")
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")

def load_geometry_config(filename):
    """
    Carga una configuración de geometría desde un archivo JSON.
    
    Args:
        filename (str): Nombre del archivo a cargar
    
    Returns:
        dict: Datos de geometría cargados
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si los datos no son válidos
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return validate_geometry_data(data)

# --- Puntos para escalar el código: Entrada de datos ---
# - Implementar una interfaz gráfica (GUI) usando tkinter o PyQt
# - Añadir soporte para importar desde archivos CAD/BIM (DXF, IFC)
# - Implementar plantillas de edificios comunes (residencial, oficinas, etc.)
# - Añadir configuración avanzada (irregularidades, voladizos, escaleras)
# - Implementar validación de normativas específicas por país
# - Añadir soporte para sistemas de unidades (métrico/imperial)
# - Implementar modo batch para análisis paramétricos