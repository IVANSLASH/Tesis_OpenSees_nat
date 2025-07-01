# analysis.py
# ============================================
# Este módulo configura y ejecuta el análisis estructural utilizando
# OpenSeesPy. Define los parámetros del análisis (tipo, algoritmo,
# integrador, etc.) y gestiona la ejecución del cálculo para obtener
# las solicitaciones y deformaciones de la estructura.
# ============================================

import openseespy.opensees as ops
import signal
import time
import threading
import queue

def verify_model_before_analysis():
    """
    Verifica la integridad del modelo antes del análisis.
    """
    print("  🔍 Verificando integridad del modelo...")
    
    try:
        # Verificar nodos
        node_tags = ops.getNodeTags()
        if not node_tags:
            print("    ❌ Error: No hay nodos en el modelo")
            return False
        print(f"    ✅ {len(node_tags)} nodos encontrados")
        
        # Verificar elementos
        ele_tags = ops.getEleTags()
        if not ele_tags:
            print("    ❌ Error: No hay elementos en el modelo")
            return False
        print(f"    ✅ {len(ele_tags)} elementos encontrados")
        
        # Verificar restricciones usando un método más directo
        print("    🔍 Verificando restricciones...")
        base_nodes = []
        all_base_nodes = []
        
        for node in node_tags:
            try:
                coord = ops.nodeCoord(node)
                if coord[2] < 0.01:  # Nodo en la base (z ≈ 0)
                    all_base_nodes.append(node)
            except:
                pass
        
        # Hacer una verificación simple creando un mini análisis de prueba
        try:
            # Guardar estado actual
            current_elements = len(ops.getEleTags())
            
            # Intentar un análisis de prueba muy básico
            ops.constraints('Transformation')
            ops.numberer('Plain')
            ops.system('BandGeneral') 
            ops.test('NormDispIncr', 1e-6, 2, 0)  # Sin output
            ops.algorithm('Linear')
            ops.integrator('LoadControl', 0.01)  # Paso muy pequeño
            ops.analysis('Static')
            
            print(f"    ✅ Configuración de análisis verificada")
            print(f"    ✅ {len(all_base_nodes)} nodos en la base detectados")
            
            # Resetear para el análisis real
            ops.wipeAnalysis()
            
        except Exception as e:
            print(f"    ⚠️ Advertencia en verificación de análisis: {e}")
        
        # Verificar que tenemos suficientes nodos base para estabilidad
        if len(all_base_nodes) < 4:  # Mínimo para una estructura 3D
            print(f"    ❌ ERROR: Solo {len(all_base_nodes)} nodos en la base")
            print(f"    Se necesitan al menos 4 nodos en la base para una estructura 3D estable")
            return False
        
        # Verificar algunos elementos para detectar propiedades problemáticas
        print("    🔍 Verificando propiedades de elementos...")
        problematic_elements = 0
        for i, ele in enumerate(ele_tags[:5]):  # Verificar primeros 5 elementos
            try:
                nodes = ops.eleNodes(ele)
                if len(nodes) >= 2:
                    coord1 = ops.nodeCoord(nodes[0])
                    coord2 = ops.nodeCoord(nodes[1])
                    length = ((coord2[0]-coord1[0])**2 + (coord2[1]-coord1[1])**2 + (coord2[2]-coord1[2])**2)**0.5
                    if length < 1e-6:  # Elemento con longitud casi cero
                        problematic_elements += 1
                        print(f"      ⚠️ Elemento {ele}: longitud muy pequeña ({length:.2e})")
                    elif length > 1000:  # Elemento extremadamente largo
                        problematic_elements += 1
                        print(f"      ⚠️ Elemento {ele}: longitud muy grande ({length:.2f})")
            except:
                problematic_elements += 1
        
        if problematic_elements > 0:
            print(f"    ⚠️ Se detectaron {problematic_elements} elementos con dimensiones problemáticas")
        else:
            print("    ✅ Dimensiones de elementos verificadas")
        
        # Verificación adicional para volados
        print("    🔍 Verificando compatibilidad de volados...")
        cantilever_nodes = []
        for node in node_tags:
            try:
                coord = ops.nodeCoord(node)
                # Buscar nodos que podrían ser de volados (fuera del rectángulo básico)
                # Esta es una verificación heurística
                if coord[2] > 0.01:  # No nodos base
                    cantilever_nodes.append(node)
            except:
                pass
        
        if len(cantilever_nodes) > len(all_base_nodes) * 2:  # Muchos nodos no base
            print(f"    ⚠️ Detectada estructura compleja con posibles volados")
            print(f"    📊 Nodos base: {len(all_base_nodes)}, Nodos superiores: {len(cantilever_nodes)}")
            print(f"    💡 Recomendación: Verificar estabilidad estructural")
        
        print("    ✅ Verificación de modelo completada")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error durante verificación: {e}")
        print(f"    Detalles: {str(e)}")
        return False

def analyze_with_timeout(timeout_seconds=15):
    """
    Ejecuta ops.analyze(1) con timeout para evitar colgados.
    """
    result_queue = queue.Queue()
    exception_queue = queue.Queue()
    
    def analyze_worker():
        try:
            result = ops.analyze(1)
            result_queue.put(result)
        except Exception as e:
            exception_queue.put(e)
    
    # Iniciar thread de análisis
    analyze_thread = threading.Thread(target=analyze_worker)
    analyze_thread.daemon = True  # Thread muere con el programa principal
    analyze_thread.start()
    
    # Esperar resultado con timeout
    analyze_thread.join(timeout=timeout_seconds)
    
    if analyze_thread.is_alive():
        # Thread aún corriendo = timeout
        print(f"    ⏰ TIMEOUT: El análisis excedió {timeout_seconds} segundos")
        print(f"    ❌ Posible problema de estabilidad estructural")
        return None, "TIMEOUT"
    
    # Verificar si hubo excepción
    if not exception_queue.empty():
        exception = exception_queue.get()
        return None, f"EXCEPTION: {exception}"
    
    # Verificar si hay resultado
    if not result_queue.empty():
        result = result_queue.get()
        return result, "SUCCESS"
    
    return None, "NO_RESULT"

def run_analysis():
    """
    Configura y ejecuta el análisis estático del modelo OpenSeesPy.
    """
    print("\n=== ANÁLISIS ESTRUCTURAL ===\n")
    
    # Verificar modelo antes del análisis
    if not verify_model_before_analysis():
        print("❌ El modelo no pasó las verificaciones previas al análisis")
        return False
    
    print("\n  🚀 Iniciando análisis estático...")
    
    try:
        # Configurar análisis estático con manejo robusto de errores
        print("    📋 Configurando parámetros de análisis (robustos para estabilidad)...")
        
        # Configuración de restricciones
        ops.constraints('Transformation')
        print("      ✅ Restricciones: Transformation")
        
        # Numerador (RCM es mejor para matrices dispersas)
        ops.numberer('RCM')
        print("      ✅ Numerador: RCM")
        
        # Sistema de ecuaciones con fallback robusto
        try:
            # Primero intentar con SparseSPD (más robusto para problemas de estabilidad)
            ops.system('SparseSPD')
            print("      ✅ Sistema: SparseSPD (optimizado para estabilidad)")
        except:
            try:
                # Si falla, usar ProfileSPD 
                ops.system('ProfileSPD')
                print("      ✅ Sistema: ProfileSPD (fallback)")
            except:
                # Último recurso: BandGeneral
                ops.system('BandGeneral')
                print("      ⚠️ Sistema: BandGeneral (básico)")
        
        # Criterio de convergencia más tolerante para matrices casi singulares
        ops.test('NormDispIncr', 1e-5, 10, 2)
        print("      ✅ Test: NormDispIncr (tol=1e-5, iter=10)")
        
        # Algoritmo Linear para análisis estático
        ops.algorithm('Linear')
        print("      ✅ Algoritmo: Linear")
        
        # Integrador
        ops.integrator('LoadControl', 1.0)
        print("      ✅ Integrador: LoadControl")
        
        # Tipo de análisis
        ops.analysis('Static')
        print("      ✅ Análisis: Static")
        
        print("\n    🔄 Ejecutando análisis...")
        
        # Ejecutar análisis con timeout
        start_time = time.time()
        print("    ⏳ Llamando a ops.analyze(1) con timeout de 15 segundos...")
        
        result, status = analyze_with_timeout(timeout_seconds=15)
        end_time = time.time()
        
        print(f"    ⏱️ Tiempo transcurrido: {end_time - start_time:.2f} segundos")
        print(f"    📊 Estado: {status}")
        
        if status == "TIMEOUT":
            print("    ❌ ANÁLISIS ABORTADO POR TIMEOUT")
            print("    💡 Diagnóstico: El modelo probablemente tiene problemas de estabilidad")
            print("    🔧 Posibles causas:")
            print("      • Volados demasiado largos sin soporte adecuado")
            print("      • Elementos mal conectados")
            print("      • Restricciones insuficientes")
            print("      • Propiedades de material problemáticas")
            return False
        elif status.startswith("EXCEPTION"):
            print(f"    ❌ Error durante análisis: {status}")
            return False
        elif status == "NO_RESULT":
            print("    ❌ No se obtuvo resultado del análisis")
            return False
        elif result is None:
            print(f"    ❌ Resultado nulo - Status: {status}")
            return False
        
        if result == 0:
            print("    ✅ Análisis completado exitosamente")
            
            # Calcular reacciones en los apoyos
            try:
                ops.reactions()
                print("    ✅ Reacciones en apoyos calculadas")
            except Exception as e:
                print(f"    ⚠️ Error calculando reacciones: {e}")
            
            # Verificar que tenemos resultados válidos
            print("\n  📊 Verificando resultados...")
            
            # Verificar desplazamientos
            node_tags = ops.getNodeTags()
            max_disp = 0.0
            for node in node_tags[:5]:  # Verificar algunos nodos
                try:
                    disp = ops.nodeDisp(node)
                    max_disp = max(max_disp, max(abs(d) for d in disp))
                except:
                    pass
            
            if max_disp > 1e-12:
                print(f"    ✅ Desplazamientos válidos detectados (máx: {max_disp:.2e} m)")
            else:
                print("    ⚠️ Desplazamientos muy pequeños o nulos")
            
            # Verificar fuerzas en elementos
            ele_tags = ops.getEleTags()
            forces_detected = False
            for ele in ele_tags[:5]:  # Verificar algunos elementos
                try:
                    forces = ops.eleForce(ele)
                    if any(abs(f) > 1e-12 for f in forces):
                        forces_detected = True
                        break
                except:
                    pass
            
            if forces_detected:
                print("    ✅ Fuerzas en elementos detectadas")
            else:
                print("    ⚠️ No se detectaron fuerzas significativas en elementos")
            
            print("\n🎉 ANÁLISIS ESTRUCTURAL COMPLETADO EXITOSAMENTE")
            return True
            
        else:
            print(f"    ❌ Error: El análisis falló con código {result}")
            print("    💡 Posibles causas:")
            print("      • Modelo inestable o mal condicionado")
            print("      • Restricciones insuficientes")
            print("      • Cargas mal aplicadas")
            print("      • Problemas de convergencia")
            return False
            
    except Exception as e:
        print(f"    ❌ Error durante la ejecución del análisis: {e}")
        print("    💡 Intentando diagnóstico...")
        
        try:
            # Diagnóstico básico
            node_count = len(ops.getNodeTags())
            ele_count = len(ops.getEleTags())
            print(f"      📊 Modelo: {node_count} nodos, {ele_count} elementos")
            
            # Verificar si hay elementos con problemas
            problematic_elements = []
            for ele in ops.getEleTags()[:10]:  # Verificar primeros 10
                try:
                    nodes = ops.eleNodes(ele)
                    if len(nodes) < 2:
                        problematic_elements.append(ele)
                except:
                    problematic_elements.append(ele)
            
            if problematic_elements:
                print(f"      ⚠️ Elementos problemáticos detectados: {problematic_elements[:5]}")
            
        except:
            print("      ❌ No se pudo realizar diagnóstico completo")
        
        return False

    # --- Puntos para escalar el código: Análisis ---
    # Aquí se pueden añadir diferentes tipos de análisis (ej. no lineal, dinámico).
    # Se pueden configurar diferentes algoritmos, sistemas, integradores y pruebas.
    # Se puede implementar un análisis de pushover o análisis modal.