import bpy
import math
import mathutils


# ─────────────────────────────────────────────────────────────────────────────
# FASE 2 — SESIÓN 1: mathutils + distribución procedural + colecciones + animación
#
# Conceptos nuevos:
#   mathutils.Vector  → posiciones y direcciones en 3D
#   mathutils.Euler   → rotaciones como ángulos (radianes) por eje
#   mathutils.Color   → colores con conversión HSV ↔ RGB integrada
#   Colecciones       → agrupar objetos en el Outliner (bpy.data.collections)
#   Empty padre       → transform compartido: rotar uno mueve a todos sus hijos
#   Cycles modifier   → loop de animación infinito y seamless en una fcurve
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────
# LIMPIEZA
# ─────────────────────────────────────────────
# Versión completa: unhide todo antes de seleccionar, y borra colecciones también.
# Sin este paso los objetos ocultos sobreviven entre ejecuciones del script.

def limpiar_escena():
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.editmode_toggle()

    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    for nombre in [c.name for c in bpy.data.collections]:
        bpy.data.collections.remove(bpy.data.collections[nombre])

    bpy.ops.outliner.orphans_purge(do_recursive=True)


# ─────────────────────────────────────────────
# COLECCIONES
# ─────────────────────────────────────────────

def crear_coleccion(nombre):
    col = bpy.data.collections.new(nombre)
    bpy.context.scene.collection.children.link(col)
    return col


def mover_a_coleccion(obj, col):
    bpy.context.scene.collection.objects.unlink(obj)
    col.objects.link(obj)


# ─────────────────────────────────────────────
# MATHUTILS — Vector / Euler / Color
# ─────────────────────────────────────────────

def explorar_vector():
    v1 = mathutils.Vector((1.0, 0.0, 0.0))
    v2 = mathutils.Vector((0.0, 1.0, 0.0))
    print("=== Vector ===")
    print(f"  v1 + v2      = {v1 + v2}")
    print(f"  v1 * 3       = {v1 * 3}")
    print(f"  dot(v1, v2)  = {v1.dot(v2)}")       # 0 → perpendiculares
    print(f"  cross(v1,v2) = {v1.cross(v2)}")     # (0,0,1) → regla mano derecha


def explorar_euler():
    rot = mathutils.Euler((math.radians(45), 0.0, math.radians(90)), 'XYZ')
    print("=== Euler ===")
    print(f"  en grados: X={math.degrees(rot.x):.1f}  Y={math.degrees(rot.y):.1f}  Z={math.degrees(rot.z):.1f}")


def explorar_color():
    c = mathutils.Color()
    c.hsv = (0.6, 0.9, 1.0)
    print("=== Color HSV → RGB ===")
    print(f"  HSV = {c.hsv}")
    print(f"  RGB = ({c.r:.3f}, {c.g:.3f}, {c.b:.3f})")


# ─────────────────────────────────────────────
# DISTRIBUCIÓN CIRCULAR
# ─────────────────────────────────────────────
# Parametrización polar de un círculo:
#   ángulo_i = (2π / N) * i
#   x = R * cos(ángulo_i),  y = R * sin(ángulo_i)
# i=0 → (R,0,0), i=N/4 → (0,R,0), gira antihorario visto desde arriba.

def posiciones_en_anillo(n, radio):
    posiciones = []
    for i in range(n):
        angulo = (2 * math.pi / n) * i
        x = radio * math.cos(angulo)
        y = radio * math.sin(angulo)
        posiciones.append(mathutils.Vector((x, y, 0.0)))
    return posiciones


# ─────────────────────────────────────────────
# MATERIALES
# ─────────────────────────────────────────────

def color_por_indice(i, total):
    c = mathutils.Color()
    c.hsv = (i / total, 0.85, 0.95)
    return (c.r, c.g, c.b, 1.0)


def crear_material(nombre, color_rgba, roughness=0.25):
    mat = bpy.data.materials.new(name=nombre)
    # use_nodes deprecado en Blender 4.x (se elimina en 6.0); los materiales
    # nuevos ya tienen node_tree activo por defecto en versiones recientes.
    if not mat.use_nodes:
        mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color_rgba
    principled.inputs["Roughness"].default_value = roughness
    return mat


# ─────────────────────────────────────────────
# ANIMACIÓN — helpers
# ─────────────────────────────────────────────

def get_fcurves(obj):
    # En Blender 4.4+ el sistema de Actions es "layered": las fcurves viven
    # dentro de action.layers[].strips[].channelbags[].fcurves
    # En versiones anteriores estaban directamente en action.fcurves.
    action = obj.animation_data.action
    if action is None:
        return []
    if hasattr(action, "layers"):
        # API nueva (Blender 4.4+)
        fcurves = []
        for layer in action.layers:
            for strip in layer.strips:
                for channelbag in strip.channelbags:
                    fcurves.extend(channelbag.fcurves)
        return fcurves
    # API antigua (Blender < 4.4)
    return list(action.fcurves)


def add_cycles_modifier(obj):
    # Cycles modifier → la animación se repite infinitamente sin duplicar keyframes.
    for fcurve in get_fcurves(obj):
        mod = fcurve.modifiers.new(type="CYCLES")
        mod.mode_before = "REPEAT"
        mod.mode_after = "REPEAT"


def set_fcurve_linear(obj):
    # LINEAR: después del último keyframe la curva sigue la pendiente → rotación eterna.
    for fc in get_fcurves(obj):
        fc.extrapolation = "LINEAR"


# ─────────────────────────────────────────────
# ANIMACIÓN 1 — Rotación del anillo completo
# ─────────────────────────────────────────────
# Técnica: parear todas las esferas a un Empty en el origen.
# Rotar el Empty rota el grupo entero sin tocar las posiciones locales de los hijos.
#
# Para un loop seamless con LINEAR extrapolation:
#   frame 1        → rotation_euler.z = 0
#   frame_end + 1  → rotation_euler.z = 2π
# El frame extra evita que el frame 1 y el último se dupliquen,
# lo que causaría una pausa perceptible en el loop.

def crear_empty_padre(nombre, col):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    empty = bpy.context.active_object
    empty.name = nombre
    mover_a_coleccion(empty, col)
    return empty


def parentar(hijo, padre):
    hijo.parent = padre
    # matrix_parent_inverse cancela el transform del padre al momento de parentar,
    # para que el hijo no "salte" de posición.
    hijo.matrix_parent_inverse = padre.matrix_world.inverted()


def animar_rotacion_z(obj, frame_end=120):
    scene = bpy.context.scene
    scene.frame_end = frame_end
    bpy.context.view_layer.objects.active = obj

    scene.frame_set(1)
    obj.rotation_euler.z = 0.0
    obj.keyframe_insert(data_path="rotation_euler", index=2)

    scene.frame_set(frame_end + 1)
    obj.rotation_euler.z = 2 * math.pi
    obj.keyframe_insert(data_path="rotation_euler", index=2)

    # LINEAR: la curva continúa girando más allá del último keyframe → loop eterno
    set_fcurve_linear(obj)

    scene.frame_set(1)


# ─────────────────────────────────────────────
# ANIMACIÓN 2 — Ola de bobbing por el anillo
# ─────────────────────────────────────────────
# Cada esfera anima su posición Z con sin(), pero con un desfase (phase) diferente.
# El desfase es proporcional al índice → la ola "viaja" alrededor del anillo.
#
#   z(t) = amplitud * sin(2π * t + phase_i)
#   donde t = frame / frame_end  (0→1 en un ciclo completo)
#         phase_i = (2π / N) * i
#
# Con Cycles modifier el ciclo se repite sin cortes.
# NOTA: la posición Z animada es LOCAL (relativa al padre),
# pero como el Empty padre solo rota en Z, Z local = Z mundial → no hay distorsión.

def animar_ola(esferas_y_fases, amplitud=0.5, frame_end=120):
    scene = bpy.context.scene
    pasos = 16    # keyframes por ciclo; más pasos = curva más suave

    for esfera, phase in esferas_y_fases:
        bpy.context.view_layer.objects.active = esfera

        for paso in range(pasos + 1):
            t = paso / pasos
            frame = round(1 + t * frame_end)
            z = amplitud * math.sin(2 * math.pi * t + phase)
            scene.frame_set(frame)
            esfera.location.z = z
            esfera.keyframe_insert(data_path="location", index=2)

        add_cycles_modifier(esfera)

    scene.frame_set(1)


# ─────────────────────────────────────────────
# CONSTRUCCIÓN DEL ANILLO
# ─────────────────────────────────────────────

def construir_anillo(n=12, radio=3.0, radio_esfera=0.4):
    col = crear_coleccion("Anillo")
    empty = crear_empty_padre("Anillo.Ctrl", col)

    posiciones = posiciones_en_anillo(n, radio)
    esferas_y_fases = []

    for i, pos in enumerate(posiciones):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radio_esfera, location=pos)
        esfera = bpy.context.active_object
        esfera.name = f"Esfera_{i:02d}"

        angulo_z = math.atan2(pos.y, pos.x)
        esfera.rotation_euler = mathutils.Euler((0.0, 0.0, angulo_z), 'XYZ')

        mat = crear_material(f"Mat_{i:02d}", color_por_indice(i, n))
        esfera.data.materials.append(mat)

        mover_a_coleccion(esfera, col)
        parentar(esfera, empty)

        phase = (2 * math.pi / n) * i
        esferas_y_fases.append((esfera, phase))

    print(f"Anillo: {n} esferas, radio={radio}")
    return empty, esferas_y_fases


# ─────────────────────────────────────────────
# LUZ Y CÁMARA
# ─────────────────────────────────────────────

def setup_escena(frame_end=120):
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = frame_end

    bpy.ops.object.light_add(type="SUN", location=(5, -5, 10))
    sol = bpy.context.active_object
    sol.name = "Sol"
    sol.data.energy = 3.0
    sol.rotation_euler = mathutils.Euler((math.radians(30), 0.0, math.radians(45)), 'XYZ')

    bpy.ops.object.camera_add(location=(0, -12, 7))
    cam = bpy.context.active_object
    cam.name = "Camara"
    cam.rotation_euler = mathutils.Euler((math.radians(55), 0.0, 0.0), 'XYZ')
    bpy.context.scene.camera = cam


# ─────────────────────────────────────────────
# EJECUCIÓN
# ─────────────────────────────────────────────

FRAME_END = 120   # 5 segundos a 24fps → 1 rotación completa + 1 ciclo de ola

explorar_vector()
explorar_euler()
explorar_color()

limpiar_escena()
setup_escena(FRAME_END)

empty, esferas_y_fases = construir_anillo(n=12, radio=3.0, radio_esfera=0.4)

animar_rotacion_z(empty, frame_end=FRAME_END)
animar_ola(esferas_y_fases, amplitud=0.5, frame_end=FRAME_END)

print("Listo. Presioná Spacebar en el viewport para ver la animación.")
