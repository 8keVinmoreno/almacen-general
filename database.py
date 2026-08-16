import os
import sqlite3


RUTA_DB = "data/inventarios.db"


def conectar():
    os.makedirs(os.path.dirname(RUTA_DB), exist_ok=True)

    return sqlite3.connect(RUTA_DB)


# ==================================================
# CREAR BASE DE DATOS
# ==================================================


def crear_base_datos():

    conexion = conectar()
    cursor = conexion.cursor()

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
# VER TODOS LOS CONTEOS
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
