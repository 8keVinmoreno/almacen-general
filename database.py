import sqlite3

RUTA_DB = "data/inventarios.db"


def conectar():
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

            sku TEXT NOT NULL,
            lote TEXT NOT NULL,
            descripcion TEXT,
            ubicacion TEXT NOT NULL,
            caducidad TEXT,

            stock_erp INTEGER,
            conteo_fisico INTEGER,
            diferencia INTEGER,
            observacion TEXT,

            UNIQUE (
                sku,
                lote,
                ubicacion
            )
        )
    """)

    conexion.commit()
    conexion.close()


# ==================================================
# GUARDAR CONTEO
# ==================================================


def guardar_conteo(
    sku,
    lote,
    descripcion,
    ubicacion,
    caducidad,
    stock_erp,
    conteo_fisico,
    observacion="",
):

    diferencia = int(conteo_fisico) - int(stock_erp)

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id
        FROM conteos
        WHERE sku = ?
        AND lote = ?
        AND ubicacion = ?
        """,
        (
            str(sku),
            str(lote),
            str(ubicacion),
        ),
    )

    registro = cursor.fetchone()

    if registro:
        cursor.execute(
            """
            UPDATE conteos

            SET descripcion = ?,
                caducidad = ?,
                stock_erp = ?,
                conteo_fisico = ?,
                diferencia = ?,
                observacion = ?

            WHERE id = ?
            """,
            (
                descripcion,
                str(caducidad),
                int(stock_erp),
                int(conteo_fisico),
                diferencia,
                observacion,
                registro[0],
            ),
        )

    else:
        cursor.execute(
            """
            INSERT INTO conteos (
                sku,
                lote,
                descripcion,
                ubicacion,
                caducidad,
                stock_erp,
                conteo_fisico,
                diferencia,
                observacion
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(sku),
                str(lote),
                descripcion,
                str(ubicacion),
                str(caducidad),
                int(stock_erp),
                int(conteo_fisico),
                diferencia,
                observacion,
            ),
        )

    conexion.commit()
    conexion.close()


# ==================================================
# SABER SI UNA LÍNEA YA FUE CONTADA
# ==================================================


def linea_ya_contada(sku, lote, ubicacion):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            conteo_fisico,
            diferencia,
            observacion

        FROM conteos

        WHERE sku = ?
        AND lote = ?
        AND ubicacion = ?
        """,
        (
            str(sku),
            str(lote),
            str(ubicacion),
        ),
    )

    resultado = cursor.fetchone()

    conexion.close()

    return resultado


# ==================================================
# VER TODOS LOS CONTEOS
# ==================================================


def ver_conteos():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            sku,
            lote,
            descripcion,
            ubicacion,
            caducidad,
            stock_erp,
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
# BORRAR TODOS LOS CONTEOS
# ==================================================


def limpiar_conteos():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM conteos")

    conexion.commit()
    conexion.close()
