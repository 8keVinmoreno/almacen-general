def limpiar_texto(valor):

    if valor is None:
        return ""

    return str(valor).strip()


# ==================================================
# BUSCAR SKU
# ==================================================


def buscar_sku(inventario, sku):

    sku_busqueda = limpiar_texto(sku)

    resultado = inventario[inventario["SKU"].astype(str).str.strip() == sku_busqueda]

    return resultado


# ==================================================
# TOTAL DE LÍNEAS
# ==================================================


def total_lineas_excel(inventario):

    return len(inventario)
