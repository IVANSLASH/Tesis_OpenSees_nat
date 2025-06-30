# El código se ejecuta sin errores y realiza un flujo de trabajo estructural integral para un pórtico tridimensional:
# (1) genera las propiedades geométricas y mecánicas de columnas y vigas, 
# (2) construye el modelo en OpenSeesPy con apoyos, transformaciones geométricas y cargas puntuales y distribuidas, 
# (3) ejecuta un análisis estático lineal, 
# (4) imprime el modelo y muestra su deformada, 
# (5) crea visualizaciones avanzadas—extrusión 3D de secciones, detalles 2D y comparación gráfica de propiedades—mediante 
#     matplotlib y opsvis, y 
# (6) traza los diagramas tridimensionales de fuerzas internas (N, Vy, Vz, My, Mz y T) con factores de escala personalizables. 
#     En conjunto, el script funciona correctamente y sirve como punto de partida sólido para futuras versiones que amplíen el tipo
#     de análisis, las geometrías o la interacción con el usuario.


# pip install openseespy opsvis matplotlib
# https://www.youtube.com/watch?v=u5BmB4bEuWk 3:52

# Importar librerías necesarias para el análisis estructural
import openseespy.opensees as ops  # Librería principal de OpenSeesPy para análisis estructural
import opsvis as opsv  # Librería para visualización de modelos OpenSeesPy
import matplotlib.pyplot as plt  # Librería para gráficos y visualización
import numpy as np  # Librería para operaciones numéricas
from mpl_toolkits.mplot3d import Axes3D  # Para gráficos 3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # Para crear polígonos 3D

# Limpiar cualquier modelo anterior y crear uno nuevo
ops.wipe()  # Limpiar el modelo anterior
ops.model('basic', '-ndm', 3, '-ndf', 6)  # Crear modelo 3D con 6 grados de libertad por nodo

# Propiedades del material y sección transversal
E  = 2040000.0    # Módulo de elasticidad (kgf/cm²)
G  =  800000.0    # Módulo de corte     (kgf/cm²)

# Dimensiones geométricas de las secciones
# Columnas (elementos verticales) - sección rectangular lx x ly
lx_col = 30.0     # Ancho de columna en dirección X (cm)
ly_col = 60.0     # Ancho de columna en dirección Y (cm)

# Vigas (elementos horizontales) - sección rectangular b x h
b_viga = 20.0     # Ancho de viga (cm)
h_viga = 35.0     # Altura de viga (cm)

# Calcular propiedades geométricas para columnas
A_col  = lx_col * ly_col                    # Área de columna (cm²)
Iz_col = (lx_col * ly_col**3) / 12         # Momento de inercia z de columna (cm⁴)
Iy_col = (ly_col * lx_col**3) / 12         # Momento de inercia y de columna (cm⁴)
J_col  = lx_col * ly_col * min(lx_col, ly_col)**2 / 3  # Módulo de torsión de columna (cm⁴)

# Calcular propiedades geométricas para vigas
A_viga  = b_viga * h_viga                   # Área de viga (cm²)
Iz_viga = (b_viga * h_viga**3) / 12        # Momento de inercia z de viga (cm⁴)
Iy_viga = (h_viga * b_viga**3) / 12        # Momento de inercia y de viga (cm⁴)
J_viga  = b_viga * h_viga * min(b_viga, h_viga)**2 / 3  # Módulo de torsión de viga (cm⁴)

# Mostrar propiedades calculadas
print("=== PROPIEDADES GEOMÉTRICAS CALCULADAS ===")
print(f"Columnas ({lx_col} x {ly_col} cm):")
print(f"  - Área: {A_col:.2f} cm²")
print(f"  - Iz: {Iz_col:.2f} cm⁴")
print(f"  - Iy: {Iy_col:.2f} cm⁴")
print(f"  - J: {J_col:.2f} cm⁴")
print(f"\nVigas ({b_viga} x {h_viga} cm):")
print(f"  - Área: {A_viga:.2f} cm²")
print(f"  - Iz: {Iz_viga:.2f} cm⁴")
print(f"  - Iy: {Iy_viga:.2f} cm⁴")
print(f"  - J: {J_viga:.2f} cm⁴")
print("=" * 50)

# Dimensiones del pórtico
Lx, Ly, Lz = 900, 900, 900  # Longitudes de los ejes x, y, z (cm)

# Carga distribuida en dirección Z (gravedad - hacia abajo)
Wz = -30  # kgf/cm (negativo = hacia abajo)

# Diccionario de condiciones de frontera para cargas distribuidas
CD = {                          # Genera un diccionario de condiciones de frontera
    5: ['-beamUniform', 0, Wz],  # Elemento 5: carga uniforme Wz en dirección Z
    6: ['-beamUniform', 0, Wz],  # Elemento 6: carga uniforme Wz en dirección Z
    7: ['-beamUniform', 0, Wz],  # Elemento 7: carga uniforme Wz en dirección Z
    8: ['-beamUniform', 0, Wz]   # Elemento 8: carga uniforme Wz en dirección Z
}

# Cargas puntuales en dirección X
Px7 = 000   # kgf (carga positiva en nodo 7)
Px8 = -000  # kgf (carga negativa en nodo 8)

# Definición de nodos del pórtico (coordenadas x, y, z)
ops.node(1,  0,    0,   0)  # Nodo 1: esquina inferior izquierda
ops.node(2,  0,   -Ly,  0)  # Nodo 2: esquina inferior derecha
ops.node(3,  Lx,  -Ly,  0)  # Nodo 3: esquina inferior posterior
ops.node(4,  Lx,   0,   0)  # Nodo 4: esquina inferior anterior
ops.node(5,  0,    0,   Lz)  # Nodo 5: esquina superior izquierda
ops.node(6,  0,   -Ly,  Lz)  # Nodo 6: esquina superior derecha
ops.node(7,  Lx,  -Ly,  Lz)  # Nodo 7: esquina superior posterior
ops.node(8,  Lx,   0,   Lz)  # Nodo 8: esquina superior anterior

# Fijar apoyos inferiores (empotrados en todos los grados de libertad)
ops.fix(1, 1, 1, 1, 1, 1, 1)  # Nodo 1: empotrado en todos los grados de libertad
ops.fix(2, 1, 1, 1, 1, 1, 1)  # Nodo 2: empotrado en todos los grados de libertad
ops.fix(3, 1, 1, 1, 1, 1, 1)  # Nodo 3: empotrado en todos los grados de libertad
ops.fix(4, 1, 1, 1, 1, 1, 1)  # Nodo 4: empotrado en todos los grados de libertad

# Tags para transformaciones geométricas
gTTagz = 1  # Transformación geométrica para el eje z (para las columnas)
gTTagx = 2  # Transformación geométrica para el eje x
gTTagy = 3  # Transformación geométrica para el eje y

# Definir transformaciones geométricas para elementos 3D
ops.geomTransf('Linear', gTTagz, *[0, -1, 0])  # Columnas (vertical) - vector auxiliar en dirección Y negativa
ops.geomTransf('Linear', gTTagx, *[0, 0, 1])   # Vigas horizontales en dirección X - vector auxiliar en dirección Z positiva
ops.geomTransf('Linear', gTTagy, *[0, 0, 1])   # Vigas horizontales en dirección Y - vector auxiliar en dirección Z positiva

# Definición de elementos estructurales
# Columnas (elementos verticales)
ops.element('elasticBeamColumn', 1, 1, 5, A_col, E, G, J_col, Iy_col, Iz_col, gTTagz)
ops.element('elasticBeamColumn', 2, 2, 6, A_col, E, G, J_col, Iy_col, Iz_col, gTTagz)
ops.element('elasticBeamColumn', 3, 3, 7, A_col, E, G, J_col, Iy_col, Iz_col, gTTagz)
ops.element('elasticBeamColumn', 4, 4, 8, A_col, E, G, J_col, Iy_col, Iz_col, gTTagz)

# Vigas en dirección Y (elementos 5 y 7)
ops.element('elasticBeamColumn', 5, 5, 6, A_viga, E, G, J_viga, Iy_viga, Iz_viga, gTTagy)
ops.element('elasticBeamColumn', 7, 8, 7, A_viga, E, G, J_viga, Iy_viga, Iz_viga, gTTagy)

# Vigas en dirección X (elementos 6 y 8)
ops.element('elasticBeamColumn', 6, 6, 7, A_viga, E, G, J_viga, Iy_viga, Iz_viga, gTTagx)
ops.element('elasticBeamColumn', 8, 5, 8, A_viga, E, G, J_viga, Iy_viga, Iz_viga, gTTagx)

# Configurar análisis estático
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Aplicar cargas puntuales en dirección X
ops.load(7, Px7,0,0,0,0,0)
ops.load(8, Px8,0,0,0,0,0)

# Aplicar cargas distribuidas según el diccionario CD
for i in CD:
    ops.eleLoad('-ele', i, '-type', CD[i][0], CD[i][1], CD[i][2])

# Configurar análisis estático
ops.constraints('Transformation')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1e-6, 6, 2)
ops.algorithm('Linear')
ops.integrator('LoadControl', 1)
ops.analysis('Static')
ops.analyze(1)

# Imprimir información del modelo
ops.printModel()

# Visualizar el modelo estructural
opsv.plot_model(axis_off=0)
plt.show()

# Visualizar deformaciones
opsv.plot_defo(sfac=100)
opsv.plot_model(axis_off=0)
plt.show()

# Función para crear visualización 3D de secciones extruidas
def plot_extruded_sections():
    """
    Crea una visualización 3D que muestra las secciones de los elementos
    extruidas a lo largo de su longitud, mostrando las dimensiones reales
    de las secciones de columnas y vigas.
    """
    fig = plt.figure(figsize=(15, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Definir colores para diferentes tipos de elementos
    colores = {
        'columna': 'blue',
        'viga_x': 'red', 
        'viga_y': 'green'
    }
    
    # Función para crear una sección rectangular extruida
    def crear_seccion_extruida(nodo1, nodo2, ancho, alto, color, nombre, tipo_elem=None):
        # Obtener coordenadas de los nodos
        coord1 = ops.nodeCoord(nodo1)
        coord2 = ops.nodeCoord(nodo2)
        
        # Vector dirección del elemento
        direccion = np.array(coord2) - np.array(coord1)
        longitud = np.linalg.norm(direccion)
        
        # Normalizar vector dirección
        if longitud > 0:
            direccion_norm = direccion / longitud
        else:
            return
        
        # Crear puntos de la sección en el origen
        # Sección rectangular centrada en el origen
        puntos_seccion = np.array([
            [-ancho/2, -alto/2, 0],
            [ancho/2, -alto/2, 0],
            [ancho/2, alto/2, 0],
            [-ancho/2, alto/2, 0]
        ])
        
        # Encontrar vectores perpendiculares para orientar la sección
        if tipo_elem is not None and tipo_elem.startswith('viga'):
            # Para vigas: altura siempre en Z, base perpendicular al eje de la viga
            # Vector Z global para la altura (eje local Y de la viga)
            perp1 = np.array([0, 0, 1])
            # Vector perpendicular al eje de la viga y a Z para la base (eje local X de la viga)
            perp2 = np.cross(direccion_norm, perp1)
            perp2 = perp2 / np.linalg.norm(perp2)
            # Recalcular perp1 para asegurar ortogonalidad
            perp1 = np.cross(perp2, direccion_norm)
        else:
            # Para columnas: mantener lógica original
            if abs(direccion_norm[2]) < 0.9:
                perp1 = np.array([0, 0, 1])
            else:
                perp1 = np.array([1, 0, 0])
            
            perp2 = np.cross(direccion_norm, perp1)
            perp2 = perp2 / np.linalg.norm(perp2)
            perp1 = np.cross(perp2, direccion_norm)
        
        # Crear matriz de transformación
        # Para vigas: perp1 = eje local Y (altura), perp2 = eje local X (base), direccion_norm = eje local Z
        R = np.column_stack([perp2, perp1, direccion_norm])
        
        # Transformar puntos de la sección
        puntos_transformados = []
        for punto in puntos_seccion:
            punto_rotado = R @ punto
            puntos_transformados.append(punto_rotado)
        
        # Crear puntos extruidos a lo largo del elemento
        num_secciones = 10
        vertices = []
        caras = []
        
        for i in range(num_secciones + 1):
            t = i / num_secciones
            posicion = np.array(coord1) + t * direccion
            
            # Puntos de la sección en esta posición
            seccion_actual = []
            for punto in puntos_transformados:
                punto_final = posicion + punto
                seccion_actual.append(punto_final)
                vertices.append(punto_final)
            
            # Crear caras entre secciones consecutivas
            if i > 0:
                idx_base = len(vertices) - 2 * len(puntos_seccion)
                idx_actual = len(vertices) - len(puntos_seccion)
                
                # Caras laterales
                for j in range(len(puntos_seccion)):
                    j_next = (j + 1) % len(puntos_seccion)
                    cara = [
                        idx_base + j,
                        idx_base + j_next,
                        idx_actual + j_next,
                        idx_actual + j
                    ]
                    caras.append(cara)
        
        # Crear colección de polígonos 3D
        if caras:
            poligonos = []
            for cara in caras:
                vertices_cara = [vertices[idx] for idx in cara]
                poligonos.append(vertices_cara)
            
            poly3d = Poly3DCollection(poligonos, alpha=0.7, facecolor=color, edgecolor='black', linewidth=0.5)
            ax.add_collection3d(poly3d)
    
    # Crear secciones extruidas para cada elemento
    # Columnas (elementos 1-4)
    for elem_id in [1, 2, 3, 4]:
        nodos = ops.eleNodes(elem_id)
        crear_seccion_extruida(nodos[0], nodos[1], lx_col, ly_col, colores['columna'], f'Columna {elem_id}', tipo_elem='columna')
    
    # Vigas en dirección Y (elementos 5 y 7)
    for elem_id in [5, 7]:
        nodos = ops.eleNodes(elem_id)
        crear_seccion_extruida(nodos[0], nodos[1], b_viga, h_viga, colores['viga_y'], f'Viga Y {elem_id}', tipo_elem='viga_y')
    
    # Vigas en dirección X (elementos 6 y 8)
    for elem_id in [6, 8]:
        nodos = ops.eleNodes(elem_id)
        crear_seccion_extruida(nodos[0], nodos[1], b_viga, h_viga, colores['viga_x'], f'Viga X {elem_id}', tipo_elem='viga_x')
    
    # Mostrar nombre y número de cada viga sobre la extrusión
    for elem_id, tipo, color in zip([5, 7, 6, 8], ['Y', 'Y', 'X', 'X'], [colores['viga_y'], colores['viga_y'], colores['viga_x'], colores['viga_x']]):
        nodos = ops.eleNodes(elem_id)
        coord1 = np.array(ops.nodeCoord(nodos[0]))
        coord2 = np.array(ops.nodeCoord(nodos[1]))
        centro = (coord1 + coord2) / 2
        ax.text(centro[0], centro[1], centro[2]+h_viga/2+20, f'Viga {tipo}{elem_id}', color=color, fontsize=10, ha='center', va='bottom', fontweight='bold')
    
    # Configurar ejes y vista
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    ax.set_title('Visualización 3D de Secciones Extruidas\nColumnas (azul), Vigas X (rojo), Vigas Y (verde)')
    
    # Ajustar límites de los ejes
    ax.set_xlim(0, Lx)
    ax.set_ylim(-Ly, 0)
    ax.set_zlim(0, Lz)
    
    # Configurar vista isométrica
    ax.view_init(elev=20, azim=45)
    
    # Agregar leyenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colores['columna'], label=f'Columnas ({lx_col}×{ly_col} cm)'),
        Patch(facecolor=colores['viga_x'], label=f'Vigas X ({b_viga}×{h_viga} cm)'),
        Patch(facecolor=colores['viga_y'], label=f'Vigas Y ({b_viga}×{h_viga} cm)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()

def plot_section_details():
    """
    Crea una visualización 2D detallada de las secciones transversales
    mostrando las dimensiones y propiedades geométricas.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Sección de columna
    ax1.set_aspect('equal')
    ax1.add_patch(plt.Rectangle((-lx_col/2, -ly_col/2), lx_col, ly_col, 
                               facecolor='lightblue', edgecolor='blue', linewidth=2))
    
    # Agregar dimensiones
    ax1.plot([-lx_col/2, -lx_col/2], [-ly_col/2-20, ly_col/2+20], 'k-', linewidth=1)
    ax1.plot([lx_col/2, lx_col/2], [-ly_col/2-20, ly_col/2+20], 'k-', linewidth=1)
    ax1.plot([-lx_col/2-20, lx_col/2+20], [-ly_col/2, -ly_col/2], 'k-', linewidth=1)
    ax1.plot([-lx_col/2-20, lx_col/2+20], [ly_col/2, ly_col/2], 'k-', linewidth=1)
    
    # Texto de dimensiones
    ax1.text(0, -ly_col/2-30, f'{lx_col} cm', ha='center', va='top', fontsize=12, fontweight='bold')
    ax1.text(-lx_col/2-30, 0, f'{ly_col} cm', ha='center', va='center', fontsize=12, fontweight='bold', rotation=90)
    
    # Propiedades
    ax1.text(0, ly_col/2+50, f'Área: {A_col:.0f} cm²', ha='center', va='bottom', fontsize=11)
    ax1.text(0, ly_col/2+30, f'Iz: {Iz_col:.0f} cm⁴', ha='center', va='bottom', fontsize=11)
    ax1.text(0, ly_col/2+10, f'Iy: {Iy_col:.0f} cm⁴', ha='center', va='bottom', fontsize=11)
    
    ax1.set_xlim(-lx_col/2-50, lx_col/2+50)
    ax1.set_ylim(-ly_col/2-50, ly_col/2+50)
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    ax1.set_title('Sección Transversal de Columna', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Sección de viga
    ax2.set_aspect('equal')
    ax2.add_patch(plt.Rectangle((-b_viga/2, -h_viga/2), b_viga, h_viga, 
                               facecolor='lightcoral', edgecolor='red', linewidth=2))
    
    # Agregar dimensiones
    ax2.plot([-b_viga/2, -b_viga/2], [-h_viga/2-15, h_viga/2+15], 'k-', linewidth=1)
    ax2.plot([b_viga/2, b_viga/2], [-h_viga/2-15, h_viga/2+15], 'k-', linewidth=1)
    ax2.plot([-b_viga/2-15, b_viga/2+15], [-h_viga/2, -h_viga/2], 'k-', linewidth=1)
    ax2.plot([-b_viga/2-15, b_viga/2+15], [h_viga/2, h_viga/2], 'k-', linewidth=1)
    
    # Texto de dimensiones
    ax2.text(0, -h_viga/2-25, f'{b_viga} cm', ha='center', va='top', fontsize=12, fontweight='bold')
    ax2.text(-b_viga/2-25, 0, f'{h_viga} cm', ha='center', va='center', fontsize=12, fontweight='bold', rotation=90)
    
    # Propiedades
    ax2.text(0, h_viga/2+40, f'Área: {A_viga:.0f} cm²', ha='center', va='bottom', fontsize=11)
    ax2.text(0, h_viga/2+20, f'Iz: {Iz_viga:.0f} cm⁴', ha='center', va='bottom', fontsize=11)
    ax2.text(0, h_viga/2+0, f'Iy: {Iy_viga:.0f} cm⁴', ha='center', va='bottom', fontsize=11)
    
    ax2.set_xlim(-b_viga/2-40, b_viga/2+40)
    ax2.set_ylim(-h_viga/2-40, h_viga/2+40)
    ax2.set_xlabel('X (cm)')
    ax2.set_ylabel('Y (cm)')
    ax2.set_title('Sección Transversal de Viga', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_section_comparison():
    """
    Crea una comparación visual de las secciones a escala real,
    mostrando las proporciones relativas entre columnas y vigas.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Comparación a escala real
    ax1.set_aspect('equal')
    
    # Posiciones para las secciones
    pos_col = (0, 0)
    pos_viga = (max(lx_col, ly_col) + 50, 0)
    
    # Dibujar sección de columna
    ax1.add_patch(plt.Rectangle((pos_col[0] - lx_col/2, pos_col[1] - ly_col/2), 
                               lx_col, ly_col, facecolor='lightblue', edgecolor='blue', linewidth=2))
    ax1.text(pos_col[0], pos_col[1] + ly_col/2 + 20, 'COLUMNA', ha='center', va='bottom', 
             fontsize=14, fontweight='bold', color='blue')
    ax1.text(pos_col[0], pos_col[1] - ly_col/2 - 20, f'{lx_col} × {ly_col} cm', ha='center', va='top', 
             fontsize=12, fontweight='bold')
    
    # Dibujar sección de viga
    ax1.add_patch(plt.Rectangle((pos_viga[0] - b_viga/2, pos_viga[1] - h_viga/2), 
                               b_viga, h_viga, facecolor='lightcoral', edgecolor='red', linewidth=2))
    ax1.text(pos_viga[0], pos_viga[1] + h_viga/2 + 20, 'VIGA', ha='center', va='bottom', 
             fontsize=14, fontweight='bold', color='red')
    ax1.text(pos_viga[0], pos_viga[1] - h_viga/2 - 20, f'{b_viga} × {h_viga} cm', ha='center', va='top', 
             fontsize=12, fontweight='bold')
    
    # Línea de escala
    escala_long = 100  # 1 metro
    ax1.plot([pos_col[0] - lx_col/2 - 30, pos_col[0] - lx_col/2 - 30 + escala_long], 
             [pos_col[1] - ly_col/2 - 40, pos_col[1] - ly_col/2 - 40], 'k-', linewidth=2)
    ax1.text(pos_col[0] - lx_col/2 - 30 + escala_long/2, pos_col[1] - ly_col/2 - 50, 
             f'{escala_long} cm', ha='center', va='top', fontsize=10, fontweight='bold')
    
    ax1.set_xlim(pos_col[0] - lx_col/2 - 60, pos_viga[0] + b_viga/2 + 60)
    ax1.set_ylim(pos_col[1] - ly_col/2 - 60, pos_col[1] + ly_col/2 + 60)
    ax1.set_title('Comparación de Secciones a Escala Real', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('X (cm)')
    ax1.set_ylabel('Y (cm)')
    
    # Comparación de propiedades
    propiedades = ['Área (cm²)', 'Iz (cm⁴)', 'Iy (cm⁴)', 'J (cm⁴)']
    valores_col = [A_col, Iz_col, Iy_col, J_col]
    valores_viga = [A_viga, Iz_viga, Iy_viga, J_viga]
    
    x = np.arange(len(propiedades))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, valores_col, width, label='Columna', color='lightblue', edgecolor='blue')
    bars2 = ax2.bar(x + width/2, valores_viga, width, label='Viga', color='lightcoral', edgecolor='red')
    
    # Agregar valores en las barras
    for bar in bars1:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.0f}', ha='center', va='bottom', fontsize=9)
    
    ax2.set_xlabel('Propiedades Geométricas')
    ax2.set_ylabel('Valor')
    ax2.set_title('Comparación de Propiedades Geométricas', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(propiedades)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# Generar visualización 3D de secciones extruidas
print("\n=== GENERANDO VISUALIZACIÓN 3D DE SECCIONES EXTRUIDAS ===")
plot_extruded_sections()

# Generar visualización detallada de secciones transversales
print("\n=== GENERANDO DETALLES DE SECCIONES TRANSVERSALES ===")
plot_section_details()

# Generar comparación de secciones
print("\n=== GENERANDO COMPARACIÓN DE SECCIONES ===")
plot_section_comparison()

# Factores de escala para los diagramas de fuerzas internas
sfacN  = 0.7e-2   # Factor de escala para fuerzas axiales
sfacVy = 5e-3     # Factor de escala para fuerzas cortantes en Y
sfacVz = 5e-3   # Factor de escala para fuerzas cortantes en Z
sfacMy = 0.5e-3   # Factor de escala para momentos en Y
sfacMz = 0.5e-3   # Factor de escala para momentos en Z
sfacT  = 5e-2     # Factor de escala para momentos torsores

# Generar diagramas de fuerzas internas en 3D
opsv.section_force_diagram_3d('N', sfacN)  # Diagrama de fuerzas axiales
plt.title('Fuerzas Axiales (kgf)')  # Título del diagrama

opsv.section_force_diagram_3d('Vy', sfacVy)  # Diagrama de fuerzas cortantes en Y
plt.title('Fuerza en el eje Y (Vy)')  # Título del diagrama

opsv.section_force_diagram_3d('Vz', sfacVz)  # Diagrama de fuerzas cortantes en Z
plt.title('Fuerza en el eje Z (Vz)')  # Título del diagrama

opsv.section_force_diagram_3d('My', sfacMy)  # Diagrama de momentos en Y
plt.title('Diagramas de momentos en eje y My')  # Título del diagrama

opsv.section_force_diagram_3d('Mz', sfacMz)  # Diagrama de momentos en Z
plt.title('Diagramas de momentos en eje z Mz')  # Título del diagrama

opsv.section_force_diagram_3d('T', sfacT)  # Diagrama de momentos torsores
plt.title('Momentos de torsión T')  # Título del diagrama
plt.show()  # Mostrar todos los diagramas 