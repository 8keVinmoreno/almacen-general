def limpiar_texto(valor):

    if valor is None:
        return ""

    return str(valor).strip()


# ==================================================
# BUSCAR MATERIAL
# ==================================================


def buscar_material(inventario, material):

    material_busqueda = limpiar_texto(material)

    resultado = inventario[
        inventario["Material"].astype(str).str.strip() == material_busqueda
    ]

    return resultado


# ==================================================
# TOTAL DE LÍNEAS
# ==================================================


def total_lineas_excel(inventario):

    return len(inventario)
