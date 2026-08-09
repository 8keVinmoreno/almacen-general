import pandas as pd


COLUMNAS_NECESARIAS = ["SKU", "Lote", "Descripcion", "Ubicacion", "Caducidad", "Stock"]


def cargar_excel(archivo):

    inventario = pd.read_excel(archivo)

    inventario.columns = inventario.columns.astype(str).str.strip()

    for columna in COLUMNAS_NECESARIAS:
        if columna not in inventario.columns:
            raise ValueError(f"Falta la columna '{columna}' en el Excel.")

    # Evitar problemas con SKU, lote y ubicación
    inventario["SKU"] = inventario["SKU"].astype(str).str.strip()

    inventario["Lote"] = inventario["Lote"].fillna("").astype(str).str.strip()

    inventario["Ubicacion"] = inventario["Ubicacion"].fillna("").astype(str).str.strip()

    return inventario
