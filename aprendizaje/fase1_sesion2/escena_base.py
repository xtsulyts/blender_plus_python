import bpy
import math


# ─────────────────────────────────────────────
# LIMPIEZA
# ─────────────────────────────────────────────

def limpiar_escena():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.outliner.orphans_purge(do_recursive=True)


# ─────────────────────────────────────────────
# FIGURAS
# ─────────────────────────────────────────────

def crear_piso():
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    piso = bpy.context.active_object
    piso.name = "Piso"
    return piso


def crear_cubo():
    bpy.ops.mesh.primitive_cube_add(size=1.2, location=(-2.5, 0, 0.6))
    obj = bpy.context.active_object
    obj.name = "Cubo"
    return obj


def crear_esfera():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0, 0, 0.7))
    obj = bpy.context.active_object
    obj.name = "Esfera"
    return obj


def crear_cilindro():
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.4, location=(2.5, 0, 0.7))
    obj = bpy.context.active_object
    obj.name = "Cilindro"
    return obj


# ─────────────────────────────────────────────
# LUZ
# ─────────────────────────────────────────────

def crear_luz():
    bpy.ops.object.light_add(type="AREA", location=(4, -4, 6))
    luz = bpy.context.active_object
    luz.name = "Luz_Principal"
    luz.data.energy = 800
    luz.data.size = 4
    luz.rotation_euler = (math.radians(45), 0, math.radians(45))
    return luz


# ─────────────────────────────────────────────
# CÁMARA
# ─────────────────────────────────────────────

def crear_camara():
    bpy.ops.object.camera_add(location=(8, -6, 5))
    cam = bpy.context.active_object
    cam.name = "Camara_Principal"
    cam.rotation_euler = (math.radians(60), 0, math.radians(53))
    bpy.context.scene.camera = cam
    return cam


# ─────────────────────────────────────────────
# MATERIALES — Principled BSDF (Tema 1.4)
# ─────────────────────────────────────────────
# Principled BSDF concentra en un solo nodo los parámetros físicos más usados:
#   Base Color  → color difuso principal
#   Metallic    → 0 = dieléctrico, 1 = metálico
#   Roughness   → 0 = espejo perfecto, 1 = completamente mate
#   Alpha       → transparencia (requiere Blend Mode Alpha)

def crear_material(nombre, base_color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True

    nodos = mat.node_tree.nodes
    principled = nodos.get("Principled BSDF")

    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness

    return mat


def asignar_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ─────────────────────────────────────────────
# KEYFRAMES — Timeline (Tema 1.5)
# ─────────────────────────────────────────────
# Keyframe = valor de una propiedad guardado en un frame específico.
# Blender interpola automáticamente entre keyframes → eso genera la animación.
# keyframe_insert(data_path, frame) guarda el valor actual de esa propiedad.

def animar_cubo(obj):
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 60

    # Aseguramos que el objeto esté activo en el contexto
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    keyframes = [(1, 0.6), (30, 3.0), (60, 0.6)]
    for frame, z in keyframes:
        scene.frame_set(frame)
        obj.location.z = z
        bpy.context.view_layer.update()
        obj.keyframe_insert(data_path="location", index=2)

    scene.frame_set(1)


# ─────────────────────────────────────────────
# EJECUCIÓN
# ─────────────────────────────────────────────

limpiar_escena()

piso = crear_piso()
cubo = crear_cubo()
esfera = crear_esfera()
cilindro = crear_cilindro()
crear_luz()
crear_camara()

# Materiales: variamos color, metallic y roughness para ver diferencias visuales
mat_piso = crear_material("Mat_Piso",    (0.8, 0.8, 0.75, 1.0), metallic=0.0, roughness=0.9)
mat_cubo = crear_material("Mat_Rojo",    (0.8, 0.1, 0.1,  1.0), metallic=0.0, roughness=0.4)
mat_esfera = crear_material("Mat_Metal", (0.9, 0.85, 0.8, 1.0), metallic=1.0, roughness=0.1)
mat_cil = crear_material("Mat_Azul",     (0.1, 0.3, 0.9,  1.0), metallic=0.0, roughness=0.7)

asignar_material(piso, mat_piso)
asignar_material(cubo, mat_cubo)
asignar_material(esfera, mat_esfera)
asignar_material(cilindro, mat_cil)

animar_cubo(cubo)

print("Escena lista: materiales Principled BSDF + animación de keyframes en el cubo.")
