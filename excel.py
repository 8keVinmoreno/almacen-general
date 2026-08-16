import pandas as pd


# ==================================================
# COLUMNAS NECESARIAS
# ==================================================

COLUMNAS_NECESARIAS = [
    "Material",
    "Texto breve de material",
    "Parte Número",
    "Ubic WM",
    "Lote",
    "FeCaduc/FePreferCons",
    "stock Disponible",
]


# ==================================================
# CARGAR EXCEL
# ==================================================


def cargar_excel(archivo):

    inventario = pd.read_excel(archivo)

    # Limpiar espacios de los nombres de columnas
    inventario.columns = inventario.columns.astype(str).str.strip()

    # ==================================================
    # COMPROBAR COLUMNAS
    # ==================================================

    for columna in COLUMNAS_NECESARIAS:
        if columna not in inventario.columns:
            raise ValueError(f"Falta la columna '{columna}' en el Excel.")

    # ==================================================
    # LIMPIAR MATERIAL
    # ==================================================

    inventario["Material"] = inventario["Material"].fillna("").astype(str).str.strip()

    # ==================================================
    # LIMPIAR TEXTO BREVE
    # ==================================================

    inventario["Texto breve de material"] = (
        inventario["Texto breve de material"].fillna("").astype(str).str.strip()
    )

    # ==================================================
    # LIMPIAR PARTE NÚMERO
    # ==================================================

    inventario["Parte Número"] = (
        inventario["Parte Número"].fillna("").astype(str).str.strip()
    )

    # ==================================================
    # LIMPIAR UBICACIÓN
    # ==================================================

    inventario["Ubic WM"] = inventario["Ubic WM"].fillna("").astype(str).str.strip()

    # ==================================================
    # LIMPIAR LOTE
    # ==================================================

    inventario["Lote"] = inventario["Lote"].fillna("").astype(str).str.strip()

    # ==================================================
    # LIMPIAR FECHA
    # ==================================================

    inventario["FeCaduc/FePreferCons"] = inventario["FeCaduc/FePreferCons"].fillna("")

    # ==================================================
    # LIMPIAR STOCK
    # ==================================================

    inventario["stock Disponible"] = (
        pd.to_numeric(
            inventario["stock Disponible"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )

    return inventario
