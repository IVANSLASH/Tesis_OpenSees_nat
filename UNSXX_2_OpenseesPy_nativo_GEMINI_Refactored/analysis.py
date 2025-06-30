# analysis.py
# ============================================
# Este módulo configura y ejecuta el análisis estructural utilizando
# OpenSeesPy. Define los parámetros del análisis (tipo, algoritmo,
# integrador, etc.) y gestiona la ejecución del cálculo para obtener
# las solicitaciones y deformaciones de la estructura.
# ============================================

import openseespy.opensees as ops

def run_analysis():
    """
    Configura y ejecuta el análisis estático del modelo OpenSeesPy.
    """
    print("\n=== ANÁLISIS ESTRUCTURAL ===\n")

    # Configurar análisis estático
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-6, 6, 2)
    ops.algorithm('Linear')
    ops.integrator('LoadControl', 1)
    ops.analysis('Static')
    ops.analyze(1)

    print("Análisis completado.")

    # --- Puntos para escalar el código: Análisis ---
    # Aquí se pueden añadir diferentes tipos de análisis (ej. no lineal, dinámico).
    # Se pueden configurar diferentes algoritmos, sistemas, integradores y pruebas.
    # Se puede implementar un análisis de pushover o análisis modal.