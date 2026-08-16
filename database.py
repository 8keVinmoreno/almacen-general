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

    # -----------------------------
    # TABLA INVENTARIO
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            material TEXT,
            texto_breve_material TEXT,
            parte_numero TEXT,
            ubic_wm TEXT,
            lote TEXT,
            fe_caduc_fe_prefer_cons TEXT,
            stock_disponible INTEGER
        )
    """)

    # -----------------------------
    # TABLA CONTEOS
    # -----------------------------

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

    # Borrar inventario anterior
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM inventario")

    for _, fila in inventario.iterrows():
        cursor.execute(
            """
            INSERT INTO inventario (
                material,
                texto_breve_material,
                parte_numero,
                ubic_wm,
                lote,
                fe_caduc_fe_prefer_cons,
                stock_disponible
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(fila["Material"]),
                str(fila["Texto breve de material"]),
                str(fila["Parte Número"]),
                str(fila["Ubic WM"]),
                str(fila["Lote"]),
                str(fila["FeCaduc/FePreferCons"]),
                int(fila["stock Disponible"]),
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
            stock_disponible

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
        ],
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

            SET texto_breve_material = ?,
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
