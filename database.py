import os
import sqlite3
import pandas as pd


RUTA_DB = "data/inventarios.db"


# ==================================================
# CONECTAR
# ==================================================


def conectar():

    os.makedirs(os.path.dirname(RUTA_DB), exist_ok=True)

    return sqlite3.connect(RUTA_DB)


# ==================================================
# CREAR BASE DE DATOS
# ==================================================


def crear_base_datos():

    conexion = conectar()
    cursor = conexion.cursor()

    # ==================================================
    # TABLA INVENTARIO
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            material TEXT,

            texto_breve_material TEXT,

            parte_numero TEXT,

            ubic_wm TEXT,

            lote TEXT,

            fe_caduc_fe_prefer_cons TEXT,

            stock_disponible INTEGER,

            unidad_medida_base TEXT

        )
    """)

    # ==================================================
    # ACTUALIZAR BASES DE DATOS ANTIGUAS
    # ==================================================

    cursor.execute("PRAGMA table_info(inventario)")

    columnas = [fila[1] for fila in cursor.fetchall()]

    if "unidad_medida_base" not in columnas:
        cursor.execute("""
            ALTER TABLE inventario
            ADD COLUMN unidad_medida_base TEXT
        """)

    # ==================================================
    # TABLA CONTEOS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conteos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            material TEXT NOT NULL,

            lote TEXT NOT NULL,

            texto_breve_material TEXT,

            parte_numero TEXT,

            ubic_wm TEXT NOT NULL,

            fe_caduc_fe_prefer_cons TEXT,

            stock_disponible INTEGER,

            conteo_fisico INTEGER,

            diferencia INTEGER,

            observacion TEXT,

            UNIQUE (
                material,
                lote,
                ubic_wm
            )

        )
    """)

    conexion.commit()
    conexion.close()


# ==================================================
# GUARDAR INVENTARIO
# ==================================================


def guardar_inventario(inventario):

    conexion = conectar()

    cursor = conexion.cursor()

    # ==================================================
    # BORRAR INVENTARIO ANTERIOR
    # ==================================================

    cursor.execute("DELETE FROM inventario")

    # ==================================================
    # INSERTAR INVENTARIO NUEVO
    # ==================================================

    for _, fila in inventario.iterrows():
        unidad_medida = fila.get("Unidad medida base", "")

        if pd.isna(unidad_medida):
            unidad_medida = ""

        cursor.execute(
            """
            INSERT INTO inventario (

                material,

                texto_breve_material,

                parte_numero,

                ubic_wm,

                lote,

                fe_caduc_fe_prefer_cons,

                stock_disponible,

                unidad_medida_base

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(fila["Material"]),
                str(fila["Texto breve de material"]),
                str(fila["Parte Número"]),
                str(fila["Ubic WM"]),
                str(fila["Lote"]),
                str(fila["FeCaduc/FePreferCons"]),
                int(fila["stock Disponible"]),
                str(unidad_medida),
            ),
        )

    conexion.commit()
    conexion.close()


# ==================================================
# OBTENER INVENTARIO
# ==================================================


def obtener_inventario():

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT

            material,

            texto_breve_material,

            parte_numero,

            ubic_wm,

            lote,

            fe_caduc_fe_prefer_cons,

            stock_disponible,

            unidad_medida_base

        FROM inventario

        ORDER BY id
    """)

    datos = cursor.fetchall()

    conexion.close()

    if not datos:
        return None

    inventario = pd.DataFrame(
        datos,
        columns=[
            "Material",
            "Texto breve de material",
            "Parte Número",
            "Ubic WM",
            "Lote",
            "FeCaduc/FePreferCons",
            "stock Disponible",
            "Unidad medida base",
        ],
    )

    # ==================================================
    # LIMPIAR UNIDAD DE MEDIDA
    # ==================================================

    inventario["Unidad medida base"] = (
        inventario["Unidad medida base"].fillna("").astype(str).str.strip()
    )

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


# ==================================================
# LIMPIAR INVENTARIO
# ==================================================


def limpiar_inventario():

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("DELETE FROM inventario")

    conexion.commit()
    conexion.close()


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

    conexion = conectar()

    cursor = conexion.cursor()

    # ==================================================
    # BUSCAR REGISTRO EXISTENTE
    # ==================================================

    cursor.execute(
        """
        SELECT id

        FROM conteos

        WHERE material = ?

        AND lote = ?

        AND ubic_wm = ?
        """,
        (
            str(material),
            str(lote),
            str(ubic_wm),
        ),
    )

    registro = cursor.fetchone()

    # ==================================================
    # ACTUALIZAR
    # ==================================================

    if registro:
        cursor.execute(
            """
            UPDATE conteos

            SET

                texto_breve_material = ?,

                parte_numero = ?,

                fe_caduc_fe_prefer_cons = ?,

                stock_disponible = ?,

                conteo_fisico = ?,

                diferencia = ?,

                observacion = ?

            WHERE id = ?
            """,
            (
                str(texto_breve_material),
                str(parte_numero),
                str(fe_caduc_fe_prefer_cons),
                int(stock_disponible),
                int(conteo_fisico),
                diferencia,
                str(observacion),
                registro[0],
            ),
        )

    # ==================================================
    # INSERTAR
    # ==================================================

    else:
        cursor.execute(
            """
            INSERT INTO conteos (

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

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(material),
                str(lote),
                str(texto_breve_material),
                str(parte_numero),
                str(ubic_wm),
                str(fe_caduc_fe_prefer_cons),
                int(stock_disponible),
                int(conteo_fisico),
                diferencia,
                str(observacion),
            ),
        )

    conexion.commit()
    conexion.close()


# ==================================================
# OBTENER TODOS LOS CONTEOS
# ==================================================


def obtener_todos_los_conteos():

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT

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

        FROM conteos

        ORDER BY id
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos


# ==================================================
# SABER SI UNA LÍNEA YA FUE CONTADA
# ==================================================


def linea_ya_contada(material, lote, ubic_wm):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT

            conteo_fisico,

            diferencia,

            observacion

        FROM conteos

        WHERE material = ?

        AND lote = ?

        AND ubic_wm = ?
        """,
        (
            str(material),
            str(lote),
            str(ubic_wm),
        ),
    )

    resultado = cursor.fetchone()

    conexion.close()

    return resultado


# ==================================================
# VER CONTEOS
# ==================================================


def ver_conteos():

    return obtener_todos_los_conteos()


# ==================================================
# BORRAR TODOS LOS CONTEOS
# ==================================================


def limpiar_conteos():

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("DELETE FROM conteos")

    conexion.commit()
    conexion.close()
