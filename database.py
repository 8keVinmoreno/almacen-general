import pandas as pd
import streamlit as st

from supabase import create_client


# ==================================================
# CONEXIÓN SUPABASE
# ==================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# ==================================================
# CREAR BASE DE DATOS
# ==================================================


def crear_base_datos():
    """
    Las tablas ya fueron creadas en Supabase.
    Se mantiene esta función porque
    streamlit_app.py la utiliza.
    """
    pass


# ==================================================
# GUARDAR INVENTARIO
# ==================================================


def guardar_inventario(inventario):

    # IMPORTANTE:
    # Esto solamente reemplaza el inventario.
    # NO toca la tabla conteos.

    supabase.table("inventario").delete().neq("id", 0).execute()

    registros = []

    for _, fila in inventario.iterrows():
        unidad_medida = fila.get("Unidad medida base", "")

        if pd.isna(unidad_medida):
            unidad_medida = ""

        registro = {
            "material": str(fila["Material"]),
            "texto_breve_material": str(fila["Texto breve de material"]),
            "parte_numero": str(fila["Parte Número"]),
            "ubic_wm": str(fila["Ubic WM"]),
            "lote": str(fila["Lote"]),
            "fe_caduc_fe_prefer_cons": str(fila["FeCaduc/FePreferCons"]),
            "stock_disponible": int(fila["stock Disponible"]),
            "unidad_medida_base": str(unidad_medida),
        }

        registros.append(registro)

    # Insertar en grupos de 500
    tamaño_lote = 500

    for inicio in range(0, len(registros), tamaño_lote):
        grupo = registros[inicio : inicio + tamaño_lote]

        if grupo:
            (supabase.table("inventario").insert(grupo).execute())


# ==================================================
# OBTENER INVENTARIO
# ==================================================


def obtener_inventario():

    todos_los_datos = []

    tamaño_pagina = 1000
    inicio = 0

    while True:
        fin = inicio + tamaño_pagina - 1

        respuesta = (
            supabase.table("inventario")
            .select("*")
            .order("id")
            .range(inicio, fin)
            .execute()
        )

        datos = respuesta.data

        if not datos:
            break

        todos_los_datos.extend(datos)

        # Si llegaron menos de 1000,
        # significa que ya llegamos al final.
        if len(datos) < tamaño_pagina:
            break

        inicio += tamaño_pagina

    if not todos_los_datos:
        return None

    inventario = pd.DataFrame(todos_los_datos)

    inventario = inventario.rename(
        columns={
            "material": "Material",
            "texto_breve_material": "Texto breve de material",
            "parte_numero": "Parte Número",
            "ubic_wm": "Ubic WM",
            "lote": "Lote",
            "fe_caduc_fe_prefer_cons": "FeCaduc/FePreferCons",
            "stock_disponible": "stock Disponible",
            "unidad_medida_base": "Unidad medida base",
        }
    )

    # ==================================================
    # ASEGURAR UNIDAD DE MEDIDA
    # ==================================================

    if "Unidad medida base" not in inventario.columns:
        inventario["Unidad medida base"] = ""

    # ==================================================
    # LIMPIAR DATOS
    # ==================================================

    inventario["Material"] = inventario["Material"].fillna("").astype(str).str.strip()

    inventario["Texto breve de material"] = (
        inventario["Texto breve de material"].fillna("").astype(str).str.strip()
    )

    inventario["Parte Número"] = (
        inventario["Parte Número"].fillna("").astype(str).str.strip()
    )

    inventario["Ubic WM"] = inventario["Ubic WM"].fillna("").astype(str).str.strip()

    inventario["Lote"] = inventario["Lote"].fillna("").astype(str).str.strip()

    inventario["Unidad medida base"] = (
        inventario["Unidad medida base"].fillna("").astype(str).str.strip()
    )

    inventario["stock Disponible"] = (
        pd.to_numeric(
            inventario["stock Disponible"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )

    return inventario


# ==================================================
# LIMPIAR INVENTARIO
# ==================================================


def limpiar_inventario():

    supabase.table("inventario").delete().neq("id", 0).execute()


# ==================================================
# GUARDAR CONTEO
# ==================================================


def guardar_conteo(
    material,
    lote,
    texto_breve_material,
    parte_numero,
    ubic_wm,
    fe_caduc_fe_prefer_cons,
    stock_disponible,
    conteo_fisico,
    observacion="",
):

    diferencia = int(conteo_fisico) - int(stock_disponible)

    datos = {
        "material": str(material),
        "lote": str(lote),
        "texto_breve_material": str(texto_breve_material),
        "parte_numero": str(parte_numero),
        "ubic_wm": str(ubic_wm),
        "fe_caduc_fe_prefer_cons": str(fe_caduc_fe_prefer_cons),
        "stock_disponible": int(stock_disponible),
        "conteo_fisico": int(conteo_fisico),
        "diferencia": diferencia,
        "observacion": str(observacion),
    }

    # ==================================================
    # BUSCAR SI YA EXISTE
    # ==================================================

    respuesta = (
        supabase.table("conteos")
        .select("id")
        .eq("material", str(material))
        .eq("lote", str(lote))
        .eq("ubic_wm", str(ubic_wm))
        .execute()
    )

    registros = respuesta.data

    # ==================================================
    # ACTUALIZAR
    # ==================================================

    if registros:
        (supabase.table("conteos").update(datos).eq("id", registros[0]["id"]).execute())

    # ==================================================
    # INSERTAR
    # ==================================================

    else:
        (supabase.table("conteos").insert(datos).execute())


# ==================================================
# OBTENER TODOS LOS CONTEOS
# ==================================================


def obtener_todos_los_conteos():

    respuesta = (
        supabase.table("conteos")
        .select(
            """
            material,
            lote,
            texto_breve_material,
            parte_numero,
            ubic_wm,
            fe_caduc_fe_prefer_cons,
            stock_disponible,
            conteo_fisico,
            diferencia,
            observacion
            """
        )
        .order("id")
        .execute()
    )

    datos = respuesta.data

    resultado = []

    for fila in datos:
        resultado.append(
            (
                fila.get("material", ""),
                fila.get("lote", ""),
                fila.get("texto_breve_material", ""),
                fila.get("parte_numero", ""),
                fila.get("ubic_wm", ""),
                fila.get("fe_caduc_fe_prefer_cons", ""),
                fila.get("stock_disponible", 0),
                fila.get("conteo_fisico", 0),
                fila.get("diferencia", 0),
                fila.get("observacion", ""),
            )
        )

    return resultado


# ==================================================
# VERIFICAR SI UNA LÍNEA YA FUE CONTADA
# ==================================================


def linea_ya_contada(
    material,
    lote,
    ubic_wm,
):

    respuesta = (
        supabase.table("conteos")
        .select("conteo_fisico, diferencia, observacion")
        .eq("material", str(material))
        .eq("lote", str(lote))
        .eq("ubic_wm", str(ubic_wm))
        .execute()
    )

    datos = respuesta.data

    if not datos:
        return None

    fila = datos[0]

    return (
        fila.get("conteo_fisico", 0),
        fila.get("diferencia", 0),
        fila.get("observacion", ""),
    )


# ==================================================
# VER CONTEOS
# ==================================================


def ver_conteos():

    return obtener_todos_los_conteos()


# ==================================================
# BORRAR TODOS LOS CONTEOS
# ==================================================


def limpiar_conteos():

    supabase.table("conteos").delete().neq("id", 0).execute()
